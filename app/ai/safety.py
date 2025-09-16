from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional
import json
import re

from app.models.content import BrandGuide


PROFANITY_LIST = {
    # Minimal placeholder list; expand as needed
    "damn",
    "hell",
}


CLAIM_KEYWORDS = {
    # Medical claims
    "cure",
    "heal",
    "diagnose",
    "treat",
    "prescribe",
    "clinical",
    "therapeutic",
    # Financial promises
    "guaranteed",
    "risk-free",
    "no risk",
    "roi",
    "returns",
    "profit assured",
    "make you rich",
}


def _find_keywords(text: str, keywords: set[str]) -> List[str]:
    found: List[str] = []
    tl = text.lower()
    for kw in keywords:
        # word boundary for single words, plain in for phrases
        if " " in kw:
            if kw in tl:
                found.append(kw)
        else:
            if re.search(rf"\b{re.escape(kw)}\b", tl):
                found.append(kw)
    return found


def check_profanity(text: str) -> List[str]:
    return _find_keywords(text, PROFANITY_LIST)


def check_claims(text: str) -> List[str]:
    return _find_keywords(text, CLAIM_KEYWORDS)


def _brand_banned_phrases(guide: Optional[BrandGuide]) -> List[str]:
    if not guide or not guide.pillars:
        return []
    try:
        data = json.loads(guide.pillars)
        if isinstance(data, dict):
            arr = data.get("banned_phrases")
            if isinstance(arr, list):
                return [str(x).lower() for x in arr]
    except Exception:
        return []
    return []


def enforce_banned_phrases(text: str, guide: Optional[BrandGuide]) -> Tuple[str, List[str]]:
    banned = _brand_banned_phrases(guide)
    if not banned:
        return text, []
    tl = text
    hits: List[str] = []
    for phrase in banned:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        if re.search(pattern, tl):
            hits.append(phrase)
            tl = re.sub(pattern, "", tl)
    # collapse whitespace after removals
    tl = re.sub(r"\s+", " ", tl).strip()
    return tl, hits


def max_len(text: str, max_words: int = 200) -> Tuple[str, bool]:
    words = text.split()
    if len(words) <= max_words:
        return text, True
    clipped = " ".join(words[:max_words])
    return clipped, False


@dataclass
class ValidationResult:
    ok: bool
    reasons: List[str]
    fixed_text: str


def validate_caption(text: str, guide: Optional[BrandGuide]) -> ValidationResult:
    reasons: List[str] = []
    fixed = text

    prof = check_profanity(fixed)
    if prof:
        reasons.append(f"profanity: {', '.join(prof)}")

    claims = check_claims(fixed)
    if claims:
        reasons.append(f"claims: {', '.join(claims)}")

    fixed, removed = enforce_banned_phrases(fixed, guide)
    if removed:
        reasons.append(f"banned: {', '.join(removed)}")

    fixed, within = max_len(fixed, 200)
    if not within:
        reasons.append("truncated_to_200_words")

    ok = len(reasons) == 0
    return ValidationResult(ok=ok, reasons=reasons, fixed_text=fixed)


