from __future__ import annotations

import json

from app.ai.safety import check_claims, validate_caption
from app.models.content import BrandGuide


def test_claim_keywords_flag_medical_and_financial():
    text = "This will cure you with guaranteed returns and clinical proof"
    hits = check_claims(text)
    assert any(h in hits for h in ["cure", "clinical"])  # medical
    assert any(h in hits for h in ["guaranteed", "returns"])  # financial


def test_banned_phrases_removed_from_caption():
    guide = BrandGuide(
        id="org1",
        org_id="org1",
        pillars=json.dumps({"banned_phrases": ["never say this", "ban me"]}),
    )
    res = validate_caption("We should never say this in copy, please ban me now", guide)
    assert "banned:" in ",".join(res.reasons)
    assert "never say this" not in res.fixed_text.lower()
    assert "ban me" not in res.fixed_text.lower()


