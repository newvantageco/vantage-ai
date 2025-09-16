from __future__ import annotations

from sqlalchemy.orm import Session

from app.optimiser.bandit import update_state, thompson_sample
from app.models.optimiser import OptimiserState


def test_thompson_sampling_prefers_higher_reward(db_session: Session):
	# Seed two arms: A with higher average reward, B with lower
	org_id = "org_test"
	A = "linkedin:post:Mon:10"
	B = "linkedin:post:Mon:11"
	# Simulate pulls
	for _ in range(10):
		update_state(db_session, org_id, A, 0.8)
		update_state(db_session, org_id, B, 0.2)
	states = db_session.query(OptimiserState).filter_by(org_id=org_id).all()
	# Sample multiple times and count picks
	picks_A = 0
	picks_B = 0
	for _ in range(200):
		k = thompson_sample(states)
		if k == A:
			picks_A += 1
		elif k == B:
			picks_B += 1
	assert picks_A > picks_B, (picks_A, picks_B)


