#!/usr/bin/env python3
"""
Comprehensive test suite for Safety Validation System.
Tests every line of function systematically.
"""

import pytest
import json
from unittest.mock import Mock, patch

from app.ai.safety import check_claims, validate_caption, ValidationResult
from app.models.content import BrandGuide


class TestSafetyValidation:
    """Comprehensive tests for safety validation functions."""

    def test_check_claims_empty_text(self):
        """Test check_claims with empty text."""
        result = check_claims("")
        assert result == []

    def test_check_claims_no_claims(self):
        """Test check_claims with text containing no claim keywords."""
        text = "This is a normal product description without any claims."
        result = check_claims(text)
        assert result == []

    def test_check_claims_medical_claims(self):
        """Test check_claims with medical claim keywords."""
        medical_texts = [
            "This will cure your illness",
            "Clinical studies prove effectiveness",
            "FDA approved treatment",
            "Medical breakthrough",
            "Therapeutic benefits",
            "Healing properties",
            "Doctor recommended",
            "Prescription strength"
        ]
        
        for text in medical_texts:
            result = check_claims(text)
            assert len(result) > 0, f"Should detect medical claims in: {text}"
            assert any(keyword in result for keyword in ["cure", "clinical", "medical", "therapeutic", "healing", "doctor", "prescription"])

    def test_check_claims_financial_claims(self):
        """Test check_claims with financial claim keywords."""
        financial_texts = [
            "Guaranteed returns on investment",
            "Make money fast",
            "Financial freedom",
            "Earn thousands daily",
            "Risk-free investment",
            "Guaranteed profit",
            "Get rich quick",
            "Financial success"
        ]
        
        for text in financial_texts:
            result = check_claims(text)
            assert len(result) > 0, f"Should detect financial claims in: {text}"
            assert any(keyword in result for keyword in ["guaranteed", "returns", "money", "financial", "earn", "profit", "rich", "success"])

    def test_check_claims_mixed_claims(self):
        """Test check_claims with both medical and financial claims."""
        text = "This will cure you with guaranteed returns and clinical proof"
        result = check_claims(text)
        
        assert len(result) > 0
        assert any(keyword in result for keyword in ["cure", "clinical"])  # medical
        assert any(keyword in result for keyword in ["guaranteed", "returns"])  # financial

    def test_check_claims_case_insensitive(self):
        """Test check_claims is case insensitive."""
        text = "GUARANTEED RETURNS AND CLINICAL PROOF"
        result = check_claims(text)
        
        assert len(result) > 0
        assert "guaranteed" in result
        assert "clinical" in result

    def test_check_claims_partial_matches(self):
        """Test check_claims with partial word matches."""
        text = "This is not a guarantee but shows clinical evidence"
        result = check_claims(text)
        
        # Should not match "guarantee" as it's not "guaranteed"
        assert "guaranteed" not in result
        # Should match "clinical"
        assert "clinical" in result

    def test_check_claims_special_characters(self):
        """Test check_claims with special characters and punctuation."""
        text = "Guaranteed! Returns... Clinical? Proof!!!"
        result = check_claims(text)
        
        assert len(result) > 0
        assert "guaranteed" in result
        assert "clinical" in result

    def test_validate_caption_no_brand_guide(self):
        """Test validate_caption without brand guide."""
        text = "This is a normal caption"
        result = validate_caption(text, None)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is True
        assert result.reasons == []
        assert result.fixed_text == text

    def test_validate_caption_with_claims_no_brand_guide(self):
        """Test validate_caption with claims but no brand guide."""
        text = "This will cure you with guaranteed returns"
        result = validate_caption(text, None)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is False
        assert "claims" in ",".join(result.reasons)
        assert result.fixed_text == text  # Should not be modified without brand guide

    def test_validate_caption_with_brand_guide_no_issues(self):
        """Test validate_caption with brand guide but no issues."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"banned_phrases": []})
        )
        
        text = "This is a normal caption"
        result = validate_caption(text, guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is True
        assert result.reasons == []
        assert result.fixed_text == text

    def test_validate_caption_with_banned_phrases(self):
        """Test validate_caption with banned phrases."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"banned_phrases": ["never say this", "ban me", "forbidden"]})
        )
        
        text = "We should never say this in copy, please ban me now"
        result = validate_caption(text, guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is False
        assert "banned" in ",".join(result.reasons)
        assert "never say this" not in result.fixed_text.lower()
        assert "ban me" not in result.fixed_text.lower()

    def test_validate_caption_with_claims_and_banned_phrases(self):
        """Test validate_caption with both claims and banned phrases."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"banned_phrases": ["never say this", "guaranteed"]})
        )
        
        text = "This will cure you with guaranteed returns, never say this"
        result = validate_caption(text, guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is False
        assert "claims" in ",".join(result.reasons)
        assert "banned" in ",".join(result.reasons)
        assert "guaranteed" not in result.fixed_text.lower()
        assert "never say this" not in result.fixed_text.lower()

    def test_validate_caption_case_insensitive_banned_phrases(self):
        """Test validate_caption with case insensitive banned phrase detection."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"banned_phrases": ["NEVER SAY THIS", "Ban Me"]})
        )
        
        text = "We should never say this in copy, please ban me now"
        result = validate_caption(text, guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is False
        assert "banned" in ",".join(result.reasons)
        assert "never say this" not in result.fixed_text.lower()
        assert "ban me" not in result.fixed_text.lower()

    def test_validate_caption_partial_banned_phrase_matches(self):
        """Test validate_caption with partial banned phrase matches."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"banned_phrases": ["never say this", "ban me"]})
        )
        
        text = "We should never say this is good, please ban me from this"
        result = validate_caption(text, guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is False
        assert "banned" in ",".join(result.reasons)
        # Should remove exact matches, not partial matches
        assert "never say this" not in result.fixed_text.lower()
        assert "ban me" not in result.fixed_text.lower()

    def test_validate_caption_empty_banned_phrases(self):
        """Test validate_caption with empty banned phrases list."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"banned_phrases": []})
        )
        
        text = "This is a normal caption"
        result = validate_caption(text, guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is True
        assert result.reasons == []
        assert result.fixed_text == text

    def test_validate_caption_malformed_brand_guide(self):
        """Test validate_caption with malformed brand guide JSON."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars="invalid json"
        )
        
        text = "This is a normal caption"
        result = validate_caption(text, guide)
        
        # Should handle malformed JSON gracefully
        assert isinstance(result, ValidationResult)
        assert result.ok is True  # Should not fail due to malformed JSON
        assert result.fixed_text == text

    def test_validate_caption_missing_banned_phrases_key(self):
        """Test validate_caption with brand guide missing banned_phrases key."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"other_key": "value"})
        )
        
        text = "This is a normal caption"
        result = validate_caption(text, guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is True
        assert result.reasons == []
        assert result.fixed_text == text

    def test_validate_caption_claims_with_brand_guide(self):
        """Test validate_caption with claims and brand guide."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"banned_phrases": []})
        )
        
        text = "This will cure you with guaranteed returns"
        result = validate_caption(text, guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is False
        assert "claims" in ",".join(result.reasons)
        assert result.fixed_text == text  # Should not be modified for claims

    def test_validate_caption_multiple_banned_phrases(self):
        """Test validate_caption with multiple banned phrases."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"banned_phrases": ["phrase1", "phrase2", "phrase3"]})
        )
        
        text = "This contains phrase1 and phrase2 but not phrase3"
        result = validate_caption(text, guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is False
        assert "banned" in ",".join(result.reasons)
        assert "phrase1" not in result.fixed_text.lower()
        assert "phrase2" not in result.fixed_text.lower()
        assert "phrase3" in result.fixed_text.lower()  # Should remain as it wasn't in the text

    def test_validate_caption_whitespace_handling(self):
        """Test validate_caption with various whitespace scenarios."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"banned_phrases": ["test phrase", "another phrase"]})
        )
        
        # Test with extra spaces
        text = "This contains test  phrase and another   phrase"
        result = validate_caption(text, guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is False
        assert "banned" in ",".join(result.reasons)
        assert "test phrase" not in result.fixed_text.lower()
        assert "another phrase" not in result.fixed_text.lower()

    def test_validate_caption_punctuation_handling(self):
        """Test validate_caption with punctuation in banned phrases."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"banned_phrases": ["test, phrase", "another-phrase"]})
        )
        
        text = "This contains test, phrase and another-phrase"
        result = validate_caption(text, guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is False
        assert "banned" in ",".join(result.reasons)
        assert "test, phrase" not in result.fixed_text.lower()
        assert "another-phrase" not in result.fixed_text.lower()

    def test_validate_caption_unicode_handling(self):
        """Test validate_caption with unicode characters."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"banned_phrases": ["test phrase"]})
        )
        
        text = "This contains test phrase with unicode: 世界 🌍"
        result = validate_caption(text, guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is False
        assert "banned" in ",".join(result.reasons)
        assert "test phrase" not in result.fixed_text.lower()
        assert "世界 🌍" in result.fixed_text  # Unicode should be preserved

    def test_validate_caption_very_long_text(self):
        """Test validate_caption with very long text."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"banned_phrases": ["banned"]})
        )
        
        # Create very long text
        long_text = "This is a very long text. " * 1000 + "banned phrase at the end"
        result = validate_caption(long_text, guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is False
        assert "banned" in ",".join(result.reasons)
        assert "banned phrase" not in result.fixed_text.lower()

    def test_validate_caption_empty_text(self):
        """Test validate_caption with empty text."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"banned_phrases": ["banned"]})
        )
        
        result = validate_caption("", guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is True
        assert result.reasons == []
        assert result.fixed_text == ""

    def test_validate_caption_none_text(self):
        """Test validate_caption with None text."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars=json.dumps({"banned_phrases": ["banned"]})
        )
        
        result = validate_caption(None, guide)
        
        assert isinstance(result, ValidationResult)
        assert result.ok is True
        assert result.reasons == []
        assert result.fixed_text == ""

    def test_validation_result_creation(self):
        """Test ValidationResult creation and properties."""
        result = ValidationResult(
            ok=True,
            reasons=["reason1", "reason2"],
            fixed_text="fixed text"
        )
        
        assert result.ok is True
        assert result.reasons == ["reason1", "reason2"]
        assert result.fixed_text == "fixed text"

    def test_validation_result_creation_false(self):
        """Test ValidationResult creation with False ok."""
        result = ValidationResult(
            ok=False,
            reasons=["error1", "error2"],
            fixed_text="corrected text"
        )
        
        assert result.ok is False
        assert result.reasons == ["error1", "error2"]
        assert result.fixed_text == "corrected text"

    def test_validation_result_empty_reasons(self):
        """Test ValidationResult creation with empty reasons."""
        result = ValidationResult(
            ok=True,
            reasons=[],
            fixed_text="text"
        )
        
        assert result.ok is True
        assert result.reasons == []
        assert result.fixed_text == "text"

    def test_validation_result_none_reasons(self):
        """Test ValidationResult creation with None reasons."""
        result = ValidationResult(
            ok=True,
            reasons=None,
            fixed_text="text"
        )
        
        assert result.ok is True
        assert result.reasons is None
        assert result.fixed_text == "text"
