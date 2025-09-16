from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import mean, pstdev
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.entities import Channel
from app.models.content import Schedule
from app.models.optimiser import ScheduleMetrics, OptimiserState


JsonDict = Dict[str, Any]


@dataclass
class ChannelMetric:
    channel_id: str
    channel_provider: str
    schedule_id: str
    ctr: float
    engagement_rate: float
    reach_norm: float
    conv_rate: float
    score: float


def _now_utc() -> datetime:
    return datetime.utcnow()


def _z_scores(values: List[float]) -> List[float]:
    if not values:
        return []
    mu = mean(values)
    sd = pstdev(values) if len(values) > 1 else 0.0
    if sd == 0:
        return [0.0 for _ in values]
    return [(v - mu) / sd for v in values]


def _composite_score(ctr: Optional[float], engagement: Optional[float], reach: Optional[float], conv: Optional[float]) -> float:
    # Simple weighted blend; weights can be tuned
    c = ctr or 0.0
    e = engagement or 0.0
    r = reach or 0.0
    v = conv or 0.0
    return 0.35 * c + 0.35 * e + 0.2 * r + 0.1 * v


def collect_last7_metrics(db: Session, org_id: str, now: Optional[datetime] = None) -> List[ChannelMetric]:
    now = now or _now_utc()
    start = now - timedelta(days=7)

    q = (
        select(
            Schedule.id.label("schedule_id"),
            Schedule.channel_id,
            Channel.provider,
            ScheduleMetrics.ctr,
            ScheduleMetrics.engagement_rate,
            ScheduleMetrics.reach_norm,
            ScheduleMetrics.conv_rate,
        )
        .join(ScheduleMetrics, ScheduleMetrics.schedule_id == Schedule.id)
        .join(Channel, Channel.id == Schedule.channel_id)
        .where(Schedule.org_id == org_id)
        .where(Schedule.scheduled_at >= start)
        .where(Schedule.scheduled_at <= now)
    )

    rows = db.execute(q).all()
    metrics: List[ChannelMetric] = []
    for row in rows:
        score = _composite_score(row.ctr, row.engagement_rate, row.reach_norm, row.conv_rate)
        metrics.append(
            ChannelMetric(
                channel_id=row.channel_id,
                channel_provider=row.provider,
                schedule_id=row.schedule_id,
                ctr=float(row.ctr or 0.0),
                engagement_rate=float(row.engagement_rate or 0.0),
                reach_norm=float(row.reach_norm or 0.0),
                conv_rate=float(row.conv_rate or 0.0),
                score=score,
            )
        )
    return metrics


def detect_winners_laggards(metrics: List[ChannelMetric]) -> Tuple[List[ChannelMetric], List[ChannelMetric]]:
    if not metrics:
        return [], []
    scores = [m.score for m in metrics]
    z = _z_scores(scores)
    # Winner if z >= +1, laggard if z <= -1
    winners: List[ChannelMetric] = []
    laggards: List[ChannelMetric] = []
    for m, zval in zip(metrics, z):
        if zval >= 1.0:
            winners.append(m)
        elif zval <= -1.0:
            laggards.append(m)
    # Fallback: at least pick top 1 and bottom 1 if empty
    if not winners and metrics:
        winners = [max(metrics, key=lambda x: x.score)]
    if not laggards and metrics:
        laggards = [min(metrics, key=lambda x: x.score)]
    return winners, laggards


def query_optimiser_deltas(db: Session, org_id: str, now: Optional[datetime] = None) -> List[JsonDict]:
    now = now or _now_utc()
    start = now - timedelta(days=7)
    # Aggregate changes over last week
    q = (
        select(
            OptimiserState.key,
            func.sum(OptimiserState.pulls).label("pulls"),
            func.sum(OptimiserState.rewards).label("rewards"),
            func.max(OptimiserState.last_action_at).label("last_action_at"),
        )
        .where(OptimiserState.org_id == org_id)
        .where((OptimiserState.last_action_at == None) | (OptimiserState.last_action_at >= start))
        .group_by(OptimiserState.key)
    )
    rows = db.execute(q).all()
    deltas: List[JsonDict] = []
    for r in rows:
        deltas.append(
            {
                "key": r.key,
                "pulls": int(r.pulls or 0),
                "rewards": float(r.rewards or 0.0),
                "last_action_at": (r.last_action_at.isoformat() if r.last_action_at else None),
            }
        )
    return deltas


def build_summary(org_id: str, metrics: List[ChannelMetric], winners: List[ChannelMetric], laggards: List[ChannelMetric], optimiser_deltas: List[JsonDict]) -> JsonDict:
    # Highlights and issues
    highlights: List[str] = []
    issues: List[str] = []

    if winners:
        top = winners[:3]
        for w in top:
            highlights.append(
                f"High performer on {w.channel_provider}: schedule {w.schedule_id} score {w.score:.2f} (CTR {w.ctr:.2%}, ER {w.engagement_rate:.2%})"
            )
    if laggards:
        bottom = laggards[:3]
        for l in bottom:
            issues.append(
                f"Underperforming on {l.channel_provider}: schedule {l.schedule_id} score {l.score:.2f} (CTR {l.ctr:.2%}, ER {l.engagement_rate:.2%})"
            )

    # Recommended actions (non-destructive, idempotent)
    actions: List[JsonDict] = []
    
    # Always ensure at least 1 action is provided
    # Clone best post to next similar slot
    if winners:
        w0 = winners[0]
        actions.append({
            "action": "clone_post",
            "schedule_id": w0.schedule_id,
            "timeslot": "Tue_19",
            "idempotency_key": f"clone_{w0.schedule_id}_{w0.channel_provider}",  # Ensure idempotency
        })
    
    # Create variants for a laggard
    if laggards:
        l0 = laggards[0]
        actions.append({
            "action": "create_variants",
            "content_id": l0.schedule_id,  # schedule_id used as proxy; UI may map to content
            "count": 3,
            "idempotency_key": f"variants_{l0.schedule_id}_{l0.channel_provider}",  # Ensure idempotency
        })
    
    # Suggest budget increase for a strong channel (stub only)
    if winners:
        strong_channel = winners[0].channel_provider
        actions.append({
            "action": "increase_budget",
            "channel": strong_channel,
            "by_pct": 15,
            "idempotency_key": f"budget_{strong_channel}_{_now_utc().strftime('%Y%m%d')}",  # Daily idempotency
        })
    
    # Fallback: if no specific actions, provide a generic optimization action
    if not actions:
        actions.append({
            "action": "optimize_schedule",
            "description": "Review and optimize posting schedule based on performance data",
            "idempotency_key": f"optimize_{org_id}_{_now_utc().strftime('%Y%m%d')}",  # Daily idempotency
        })

    return {
        "org_id": org_id,
        "generated_at": _now_utc().isoformat(),
        "highlights": highlights,
        "issues": issues,
        "optimiser_deltas": optimiser_deltas,
        "actions": actions,
    }


def generate_weekly_brief(db: Session, org_id: str, now: Optional[datetime] = None) -> JsonDict:
    metrics = collect_last7_metrics(db=db, org_id=org_id, now=now)
    winners, laggards = detect_winners_laggards(metrics)
    deltas = query_optimiser_deltas(db=db, org_id=org_id, now=now)
    return build_summary(org_id=org_id, metrics=metrics, winners=winners, laggards=laggards, optimiser_deltas=deltas)


# Convenience fake generator for DRY_RUN/testing without DB metrics
def generate_weekly_brief_fake(org_id: str) -> JsonDict:
    fake_metrics = [
        ChannelMetric(channel_id="ch1", channel_provider="tiktok", schedule_id="s1", ctr=0.045, engagement_rate=0.12, reach_norm=0.8, conv_rate=0.01, score=_composite_score(0.045,0.12,0.8,0.01)),
        ChannelMetric(channel_id="ch2", channel_provider="linkedin", schedule_id="s2", ctr=0.010, engagement_rate=0.03, reach_norm=0.5, conv_rate=0.004, score=_composite_score(0.01,0.03,0.5,0.004)),
        ChannelMetric(channel_id="ch3", channel_provider="meta", schedule_id="s3", ctr=0.025, engagement_rate=0.07, reach_norm=0.6, conv_rate=0.006, score=_composite_score(0.025,0.07,0.6,0.006)),
    ]
    winners, laggards = detect_winners_laggards(fake_metrics)
    deltas = [
        {"key": "tiktok:evening", "pulls": 5, "rewards": 1.8, "last_action_at": None},
        {"key": "linkedin:mornings", "pulls": 3, "rewards": 0.3, "last_action_at": None},
    ]
    return build_summary(org_id=org_id, metrics=fake_metrics, winners=winners, laggards=laggards, optimiser_deltas=deltas)


