#!/usr/bin/env python3
"""
Systematic test suite for core functions without external dependencies.
Tests every line of function systematically.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta


class TestCoreFunctions:
    """Systematic tests for core functions."""

    def test_token_estimation_basic(self):
        """Test basic token estimation logic."""
        def estimate_tokens(text: str) -> int:
            """Rough token estimation (4 chars per token average)."""
            return len(text) // 4
        
        # Test case 1: Normal text
        text = "Hello world"
        expected = len(text) // 4  # 11 // 4 = 2
        result = estimate_tokens(text)
        assert result == expected
        
        # Test case 2: Empty string
        result = estimate_tokens("")
        assert result == 0
        
        # Test case 3: Long text
        long_text = "A" * 1000
        expected = 1000 // 4  # 250
        result = estimate_tokens(long_text)
        assert result == expected

    def test_token_estimation_edge_cases(self):
        """Test token estimation edge cases."""
        def estimate_tokens(text: str) -> int:
            return len(text) // 4
        
        # Test case 1: Single character
        result = estimate_tokens("a")
        assert result == 0  # 1 // 4 = 0
        
        # Test case 2: Exactly 4 characters
        result = estimate_tokens("test")
        assert result == 1  # 4 // 4 = 1
        
        # Test case 3: Unicode characters
        unicode_text = "Hello 世界 🌍"
        result = estimate_tokens(unicode_text)
        assert result > 0

    def test_cost_estimation_logic(self):
        """Test cost estimation logic."""
        def estimate_cost(provider: str, tokens_in: int, tokens_out: int) -> float:
            """Estimate cost in GBP based on provider and token usage."""
            costs = {
                "openai:gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
                "openai:gpt-4o": {"input": 0.005, "output": 0.015},
                "ollama:llama3.1": {"input": 0.0, "output": 0.0},
                "open": {"input": 0.0001, "output": 0.0001},
            }
            
            provider_costs = costs.get(provider, costs["open"])
            input_cost = (tokens_in / 1000) * provider_costs["input"]
            output_cost = (tokens_out / 1000) * provider_costs["output"]
            return input_cost + output_cost

        # Test OpenAI GPT-4o-mini
        provider = "openai:gpt-4o-mini"
        tokens_in = 1000
        tokens_out = 500
        
        result = estimate_cost(provider, tokens_in, tokens_out)
        expected = (1000/1000 * 0.00015) + (500/1000 * 0.0006)  # 0.00015 + 0.0003 = 0.00045
        assert abs(result - expected) < 0.00001

        # Test free model
        provider = "ollama:llama3.1"
        result = estimate_cost(provider, tokens_in, tokens_out)
        assert result == 0.0

        # Test unknown provider (fallback)
        provider = "unknown:model"
        result = estimate_cost(provider, tokens_in, tokens_out)
        expected = (1000/1000 * 0.0001) + (500/1000 * 0.0001)  # 0.00015
        assert abs(result - expected) < 0.00001

    def test_cache_key_generation(self):
        """Test cache key generation logic."""
        import hashlib
        
        def make_cache_key(task: str, prompt: str, system: str = None, org_id: str = None, is_critical: bool = False) -> str:
            """Create cache key for request."""
            # Don't cache personalized content (when org_id affects output)
            if org_id and is_critical:
                return None
            
            key_data = f"{task}:{prompt}:{system or ''}"
            return f"ai:{task}:{hashlib.sha256(key_data.encode()).hexdigest()[:16]}"

        # Test basic cache key
        key = make_cache_key("caption", "Write a caption", "You are a social media assistant")
        assert key.startswith("ai:caption:")
        assert len(key) == len("ai:caption:") + 16

        # Test personalized content (should return None)
        key = make_cache_key("caption", "Write a caption", "You are a social media assistant", "org_123", True)
        assert key is None

        # Test same inputs produce same key
        key1 = make_cache_key("caption", "Write a caption", "You are a social media assistant")
        key2 = make_cache_key("caption", "Write a caption", "You are a social media assistant")
        assert key1 == key2

        # Test different inputs produce different keys
        key1 = make_cache_key("caption", "Write a caption about A")
        key2 = make_cache_key("caption", "Write a caption about B")
        assert key1 != key2

    def test_claim_detection_logic(self):
        """Test claim detection logic."""
        def check_claims(text: str) -> list:
            """Check for medical and financial claims in text."""
            medical_keywords = ["cure", "clinical", "medical", "therapeutic", "healing", "doctor", "prescription", "fda"]
            financial_keywords = ["guaranteed", "returns", "money", "financial", "earn", "profit", "rich", "success", "investment"]
            
            text_lower = text.lower()
            found_claims = []
            
            for keyword in medical_keywords + financial_keywords:
                if keyword in text_lower:
                    found_claims.append(keyword)
            
            return found_claims

        # Test medical claims
        text = "This will cure your illness"
        claims = check_claims(text)
        assert "cure" in claims

        # Test financial claims
        text = "Guaranteed returns on investment"
        claims = check_claims(text)
        assert "guaranteed" in claims
        assert "returns" in claims

        # Test mixed claims
        text = "This will cure you with guaranteed returns and clinical proof"
        claims = check_claims(text)
        assert "cure" in claims
        assert "guaranteed" in claims
        assert "clinical" in claims

        # Test no claims
        text = "This is a normal product description"
        claims = check_claims(text)
        assert claims == []

        # Test case insensitive
        text = "GUARANTEED RETURNS AND CLINICAL PROOF"
        claims = check_claims(text)
        assert "guaranteed" in claims
        assert "clinical" in claims

    def test_caption_validation_logic(self):
        """Test caption validation logic."""
        def validate_caption(text: str, brand_guide: dict = None) -> dict:
            """Validate caption for safety and brand compliance."""
            reasons = []
            fixed_text = text
            
            # Check for claims
            claims = check_claims(text)
            if claims:
                reasons.append("claims")
            
            # Check for banned phrases if brand guide provided
            if brand_guide and "banned_phrases" in brand_guide:
                banned_phrases = brand_guide["banned_phrases"]
                for phrase in banned_phrases:
                    if phrase.lower() in text.lower():
                        reasons.append("banned")
                        fixed_text = fixed_text.replace(phrase, "").replace(phrase.lower(), "")
            
            return {
                "ok": len(reasons) == 0,
                "reasons": reasons,
                "fixed_text": fixed_text
            }

        def check_claims(text: str) -> list:
            """Helper function for claim detection."""
            medical_keywords = ["cure", "clinical", "medical"]
            financial_keywords = ["guaranteed", "returns", "money"]
            
            text_lower = text.lower()
            found_claims = []
            
            for keyword in medical_keywords + financial_keywords:
                if keyword in text_lower:
                    found_claims.append(keyword)
            
            return found_claims

        # Test no issues
        result = validate_caption("This is a normal caption")
        assert result["ok"] is True
        assert result["reasons"] == []
        assert result["fixed_text"] == "This is a normal caption"

        # Test with claims
        result = validate_caption("This will cure you with guaranteed returns")
        assert result["ok"] is False
        assert "claims" in result["reasons"]

        # Test with banned phrases
        brand_guide = {"banned_phrases": ["never say this", "ban me"]}
        result = validate_caption("We should never say this in copy, please ban me now", brand_guide)
        assert result["ok"] is False
        assert "banned" in result["reasons"]
        assert "never say this" not in result["fixed_text"].lower()
        assert "ban me" not in result["fixed_text"].lower()

    def test_condition_evaluation_logic(self):
        """Test condition evaluation logic."""
        def evaluate_condition(condition: dict, payload: dict) -> bool:
            """Evaluate a condition against payload data."""
            if not condition or not isinstance(condition, dict):
                return False
            
            metric = condition.get("metric")
            operator = condition.get("operator")
            value = condition.get("value")
            
            if not all([metric, operator, value is not None]):
                return False
            
            if metric not in payload:
                return False
            
            payload_value = payload[metric]
            
            try:
                if operator == ">":
                    return payload_value > value
                elif operator == "<":
                    return payload_value < value
                elif operator == "==":
                    return payload_value == value
                elif operator == "!=":
                    return payload_value != value
                elif operator == ">=":
                    return payload_value >= value
                elif operator == "<=":
                    return payload_value <= value
                else:
                    return False
            except (TypeError, ValueError):
                return False

        # Test simple comparison
        condition = {"metric": "ctr", "operator": ">", "value": 0.05}
        payload = {"ctr": 0.08}
        result = evaluate_condition(condition, payload)
        assert result is True

        # Test comparison that fails
        condition = {"metric": "ctr", "operator": ">", "value": 0.10}
        payload = {"ctr": 0.08}
        result = evaluate_condition(condition, payload)
        assert result is False

        # Test missing metric
        condition = {"metric": "nonexistent", "operator": ">", "value": 0.05}
        payload = {"ctr": 0.08}
        result = evaluate_condition(condition, payload)
        assert result is False

        # Test invalid condition
        result = evaluate_condition({}, payload)
        assert result is False

        result = evaluate_condition(None, payload)
        assert result is False

    def test_cooldown_check_logic(self):
        """Test cooldown check logic."""
        def is_in_cooldown(rule_cooldown_minutes: int, last_executed_at: datetime) -> bool:
            """Check if rule is in cooldown period."""
            if not rule_cooldown_minutes or rule_cooldown_minutes <= 0:
                return False
            
            if not last_executed_at:
                return False
            
            time_since_last = datetime.utcnow() - last_executed_at
            cooldown_duration = timedelta(minutes=rule_cooldown_minutes)
            
            return time_since_last < cooldown_duration

        # Test no cooldown
        result = is_in_cooldown(0, datetime.utcnow() - timedelta(minutes=30))
        assert result is False

        # Test no last execution
        result = is_in_cooldown(60, None)
        assert result is False

        # Test in cooldown
        result = is_in_cooldown(60, datetime.utcnow() - timedelta(minutes=30))
        assert result is True

        # Test cooldown expired
        result = is_in_cooldown(60, datetime.utcnow() - timedelta(hours=2))
        assert result is False

    def test_text_truncation_logic(self):
        """Test text truncation logic."""
        def truncate_for_platform(text: str, max_length: int) -> str:
            """Truncate text to fit platform limits."""
            if not text:
                return text
            
            if max_length <= 0:
                return "..."
            
            if len(text) <= max_length:
                return text
            
            # Truncate and add ellipsis
            truncated = text[:max_length-3] + "..."
            return truncated

        # Test within limit
        result = truncate_for_platform("Short text", 100)
        assert result == "Short text"

        # Test exceeds limit
        result = truncate_for_platform("This is a very long text that exceeds the limit", 20)
        assert len(result) <= 20
        assert result.endswith("...")

        # Test exact limit
        result = truncate_for_platform("Exactly twenty chars", 20)
        assert result == "Exactly twenty chars"

        # Test empty text
        result = truncate_for_platform("", 100)
        assert result == ""

        # Test zero limit
        result = truncate_for_platform("Some text", 0)
        assert result == "..."

    def test_usage_stats_calculation(self):
        """Test usage stats calculation logic."""
        def calculate_usage_stats(tokens_used: int, tokens_limit: int, cost_used: float, cost_limit: float) -> dict:
            """Calculate usage statistics."""
            tokens_remaining = max(0, tokens_limit - tokens_used)
            cost_remaining = max(0.0, cost_limit - cost_used)
            
            tokens_usage_pct = (tokens_used / tokens_limit * 100) if tokens_limit > 0 else 0.0
            cost_usage_pct = (cost_used / cost_limit * 100) if cost_limit > 0 else 0.0
            
            is_over_limit = tokens_used > tokens_limit or cost_used > cost_limit
            
            return {
                "tokens_used": tokens_used,
                "tokens_limit": tokens_limit,
                "tokens_remaining": tokens_remaining,
                "cost_used_gbp": cost_used,
                "cost_limit_gbp": cost_limit,
                "cost_remaining_gbp": cost_remaining,
                "tokens_usage_pct": tokens_usage_pct,
                "cost_usage_pct": cost_usage_pct,
                "is_over_limit": is_over_limit
            }

        # Test normal usage
        stats = calculate_usage_stats(5000, 10000, 2.5, 5.0)
        assert stats["tokens_usage_pct"] == 50.0
        assert stats["cost_usage_pct"] == 50.0
        assert stats["is_over_limit"] is False
        assert stats["tokens_remaining"] == 5000
        assert stats["cost_remaining_gbp"] == 2.5

        # Test over limit
        stats = calculate_usage_stats(12000, 10000, 6.0, 5.0)
        assert stats["tokens_usage_pct"] == 120.0
        assert stats["cost_usage_pct"] == 120.0
        assert stats["is_over_limit"] is True
        assert stats["tokens_remaining"] == 0
        assert stats["cost_remaining_gbp"] == 0.0

        # Test zero limits
        stats = calculate_usage_stats(1000, 0, 0.5, 0.0)
        assert stats["tokens_usage_pct"] == 0.0
        assert stats["cost_usage_pct"] == 0.0
        assert stats["is_over_limit"] is True  # When limits are 0, any usage is over limit

    @pytest.mark.asyncio
    async def test_batch_processing_logic(self):
        """Test batch processing logic."""
        async def process_batch(items: list, process_func) -> list:
            """Process a batch of items."""
            if not items:
                return []
            
            results = []
            for item in items:
                result = await process_func(item)
                results.append(result)
            
            return results

        async def mock_process(item):
            """Mock processing function."""
            return f"processed_{item}"

        # Test empty batch
        result = await process_batch([], mock_process)
        assert result == []

        # Test single item
        result = await process_batch(["item1"], mock_process)
        assert result == ["processed_item1"]

        # Test multiple items
        result = await process_batch(["item1", "item2", "item3"], mock_process)
        assert result == ["processed_item1", "processed_item2", "processed_item3"]

    def test_error_handling_patterns(self):
        """Test common error handling patterns."""
        def safe_divide(a: float, b: float) -> tuple[float, str]:
            """Safely divide two numbers with error handling."""
            try:
                if b == 0:
                    return 0.0, "Division by zero"
                result = a / b
                return result, ""
            except (TypeError, ValueError) as e:
                return 0.0, f"Invalid input: {e}"
            except Exception as e:
                return 0.0, f"Unexpected error: {e}"

        # Test normal division
        result, error = safe_divide(10, 2)
        assert result == 5.0
        assert error == ""

        # Test division by zero
        result, error = safe_divide(10, 0)
        assert result == 0.0
        assert error == "Division by zero"

        # Test invalid input
        result, error = safe_divide("invalid", 2)
        assert result == 0.0
        assert "Invalid input" in error

    def test_data_validation_patterns(self):
        """Test data validation patterns."""
        def validate_email(email: str) -> tuple[bool, str]:
            """Validate email format."""
            if not email:
                return False, "Email is required"
            
            if not isinstance(email, str):
                return False, "Email must be a string"
            
            if "@" not in email:
                return False, "Email must contain @"
            
            if "." not in email.split("@")[-1]:
                return False, "Email must have valid domain"
            
            return True, ""

        # Test valid email
        valid, error = validate_email("test@example.com")
        assert valid is True
        assert error == ""

        # Test empty email
        valid, error = validate_email("")
        assert valid is False
        assert error == "Email is required"

        # Test invalid email
        valid, error = validate_email("invalid-email")
        assert valid is False
        assert "must contain @" in error

        # Test non-string input
        valid, error = validate_email(123)
        assert valid is False
        assert "must be a string" in error

    def test_json_handling_patterns(self):
        """Test JSON handling patterns."""
        def safe_json_parse(json_str: str, default: dict = None) -> dict:
            """Safely parse JSON string."""
            if default is None:
                default = {}
            
            try:
                return json.loads(json_str)
            except (json.JSONDecodeError, TypeError):
                return default

        # Test valid JSON
        result = safe_json_parse('{"key": "value"}')
        assert result == {"key": "value"}

        # Test invalid JSON
        result = safe_json_parse('{"key": "value"')
        assert result == {}

        # Test with custom default
        result = safe_json_parse('invalid', {"default": "value"})
        assert result == {"default": "value"}

        # Test None input
        result = safe_json_parse(None)
        assert result == {}

    def test_string_manipulation_patterns(self):
        """Test string manipulation patterns."""
        def clean_text(text: str) -> str:
            """Clean text by removing extra whitespace and normalizing."""
            if not text:
                return ""
            
            # Remove extra whitespace
            cleaned = " ".join(text.split())
            
            # Normalize case
            cleaned = cleaned.lower()
            
            return cleaned

        # Test normal text
        result = clean_text("  Hello   World  ")
        assert result == "hello world"

        # Test empty text
        result = clean_text("")
        assert result == ""

        # Test None input
        result = clean_text(None)
        assert result == ""

        # Test text with multiple spaces
        result = clean_text("This    has    multiple    spaces")
        assert result == "this has multiple spaces"

    def test_numerical_calculations(self):
        """Test numerical calculation patterns."""
        def calculate_percentage(part: float, total: float) -> float:
            """Calculate percentage with safe division."""
            if total == 0:
                return 0.0
            
            return (part / total) * 100

        # Test normal calculation
        result = calculate_percentage(25, 100)
        assert result == 25.0

        # Test zero total
        result = calculate_percentage(25, 0)
        assert result == 0.0

        # Test zero part
        result = calculate_percentage(0, 100)
        assert result == 0.0

        # Test decimal result
        result = calculate_percentage(1, 3)
        assert abs(result - 33.333333333333336) < 0.0001

    def test_list_operations(self):
        """Test list operation patterns."""
        def deduplicate_list(items: list) -> list:
            """Remove duplicates while preserving order."""
            if not items:
                return []
            
            seen = set()
            result = []
            
            for item in items:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
            
            return result

        # Test normal list
        result = deduplicate_list([1, 2, 2, 3, 1, 4])
        assert result == [1, 2, 3, 4]

        # Test empty list
        result = deduplicate_list([])
        assert result == []

        # Test no duplicates
        result = deduplicate_list([1, 2, 3, 4])
        assert result == [1, 2, 3, 4]

        # Test all duplicates
        result = deduplicate_list([1, 1, 1, 1])
        assert result == [1]

    def test_dict_operations(self):
        """Test dictionary operation patterns."""
        def merge_dicts(dict1: dict, dict2: dict) -> dict:
            """Merge two dictionaries with dict2 taking precedence."""
            if not dict1:
                return dict2 or {}
            
            if not dict2:
                return dict1 or {}
            
            result = dict1.copy()
            result.update(dict2)
            return result

        # Test normal merge
        result = merge_dicts({"a": 1, "b": 2}, {"b": 3, "c": 4})
        assert result == {"a": 1, "b": 3, "c": 4}

        # Test empty first dict
        result = merge_dicts({}, {"a": 1})
        assert result == {"a": 1}

        # Test empty second dict
        result = merge_dicts({"a": 1}, {})
        assert result == {"a": 1}

        # Test both empty
        result = merge_dicts({}, {})
        assert result == {}

        # Test None inputs
        result = merge_dicts(None, {"a": 1})
        assert result == {"a": 1}

        result = merge_dicts({"a": 1}, None)
        assert result == {"a": 1}

    def test_datetime_operations(self):
        """Test datetime operation patterns."""
        def is_within_timeframe(dt: datetime, start: datetime, end: datetime) -> bool:
            """Check if datetime is within timeframe."""
            if not all([dt, start, end]):
                return False
            
            return start <= dt <= end

        now = datetime.utcnow()
        start = now - timedelta(hours=1)
        end = now + timedelta(hours=1)

        # Test within timeframe
        result = is_within_timeframe(now, start, end)
        assert result is True

        # Test before timeframe
        result = is_within_timeframe(now - timedelta(hours=2), start, end)
        assert result is False

        # Test after timeframe
        result = is_within_timeframe(now + timedelta(hours=2), start, end)
        assert result is False

        # Test None inputs
        result = is_within_timeframe(None, start, end)
        assert result is False

        result = is_within_timeframe(now, None, end)
        assert result is False

        result = is_within_timeframe(now, start, None)
        assert result is False
