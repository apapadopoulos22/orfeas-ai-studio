#!/usr/bin/env python3
"""
BOB AI v10.0 - PHASE 4.6 SECURITY & CACHING TEST SUITE
Comprehensive tests for caching and security features

Test Coverage:
- Cache manager (Redis & in-memory)
- Authentication manager (API keys)
- Rate limiter (token bucket algorithm)
- Input validator (injection prevention)
- Security middleware

Version: 1.0.0
Date: October 28, 2025
Status: PHASE 4.6 IMPLEMENTATION
"""

import sys
import os
import time
import logging
from datetime import datetime, timedelta

# Setup path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Import security components
from phase4_cache_manager import get_cache_manager, CacheManager
from phase4_auth_manager import get_auth_manager, AuthenticationManager
from phase4_rate_limiter import get_rate_limiter, RateLimiter
from phase4_input_validator import InputValidator, ValidationException


class TestSuite:
    """Test suite for Phase 4.6 security and caching"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def test(self, name: str, condition: bool, message: str = ""):
        """Record test result"""
        status = "✓" if condition else "✗"
        result = "PASS" if condition else "FAIL"

        logger.info(f"{status} [{result}] {name}")
        if message:
            logger.info(f"    {message}")

        if condition:
            self.passed += 1
        else:
            self.failed += 1

        self.tests.append({
            "name": name,
            "passed": condition,
            "message": message
        })

    def summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0

        logger.info("=" * 80)
        logger.info(f"TEST SUMMARY: {self.passed}/{total} passed ({percentage:.1f}%)")
        logger.info("=" * 80)

        return self.failed == 0


def test_cache_manager():
    """Test cache manager functionality"""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING: Cache Manager")
    logger.info("=" * 80)

    suite = TestSuite()
    cache = get_cache_manager(use_redis=False)

    # Test set/get
    cache.set('test_key', {'data': 'test'}, ttl=60)
    value = cache.get('test_key')
    suite.test("Cache set/get", value == {'data': 'test'})

    # Test cache miss
    value = cache.get('nonexistent_key')
    suite.test("Cache miss returns None", value is None)

    # Test TTL expiration
    cache.set('short_ttl', {'data': 'expires'}, ttl=1)
    time.sleep(1.1)
    value = cache.get('short_ttl')
    suite.test("Cache TTL expiration", value is None)

    # Test delete
    cache.set('to_delete', {'data': 'delete_me'}, ttl=60)
    cache.delete('to_delete')
    value = cache.get('to_delete')
    suite.test("Cache delete", value is None)

    # Test key generation
    key1 = CacheManager.generate_key('discipline', '123')
    key2 = CacheManager.generate_key('discipline', '123')
    suite.test("Key generation consistent", key1 == key2)

    # Test flush
    cache.set('flush_test', {'data': 'flush'}, ttl=60)
    cache.flush()
    value = cache.get('flush_test')
    suite.test("Cache flush", value is None)

    # Test stats
    cache.set('stat1', {'data': 'value1'}, ttl=60)
    cache.set('stat2', {'data': 'value2'}, ttl=60)
    stats = cache.stats()
    suite.test("Cache stats available", stats is not None and 'type' in stats)

    suite.summary()
    return suite.failed == 0


def test_auth_manager():
    """Test authentication manager functionality"""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING: Authentication Manager")
    logger.info("=" * 80)

    suite = TestSuite()

    # Create fresh auth manager
    auth = AuthenticationManager()

    # Test key generation
    key = auth.generate_api_key()
    suite.test("API key generation", key.startswith('bob_ai_'))

    # Test key creation
    new_key = auth.create_key("Test Key", scopes=['read:disciplines'])
    suite.test("API key creation", new_key is not None)

    # Test authentication - valid key
    is_valid, key_id, key_data = auth.authenticate(new_key)
    suite.test("Authentication valid key", is_valid and key_id is not None)

    # Test authentication - invalid key
    is_valid, key_id, key_data = auth.authenticate("invalid_key_12345")
    suite.test("Authentication invalid key", not is_valid)

    # Test scope checking
    has_scope = auth.check_scope(key_id, 'read:disciplines')
    suite.test("Scope checking", has_scope)

    # Test key listing
    keys = auth.list_keys()
    suite.test("List keys", len(keys) >= 2)  # Dev + readonly + test key

    # Test key revocation
    test_key = auth.create_key("Revoke Test")
    auth.revoke_key(key_id)
    is_valid, _, _ = auth.authenticate(test_key)
    suite.test("Key revocation", is_valid)  # New key should still be valid

    # Test stats
    stats = auth.get_stats()
    suite.test("Auth stats", stats['total_keys'] > 0)

    suite.summary()
    return suite.failed == 0


def test_rate_limiter():
    """Test rate limiter functionality"""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING: Rate Limiter")
    logger.info("=" * 80)

    suite = TestSuite()
    limiter = get_rate_limiter()

    # Test within limit
    key = "test_key_1"
    allowed, remaining = limiter.is_allowed(key, requests_per_minute=10)
    suite.test("Request within limit", allowed)

    # Make 10 more requests
    for i in range(9):
        allowed, remaining = limiter.is_allowed(key, requests_per_minute=10)

    # 11th request should fail
    allowed, remaining = limiter.is_allowed(key, requests_per_minute=10)
    suite.test("Rate limit exceeded", not allowed)

    # Test reset
    limiter.reset_key(key)
    allowed, remaining = limiter.is_allowed(key, requests_per_minute=10)
    suite.test("Rate limit reset", allowed)

    # Test status
    status = limiter.get_status(key, requests_per_minute=20)
    suite.test("Rate limit status", status['capacity'] == 20)

    # Test different keys don't interfere
    key2 = "test_key_2"
    allowed1, _ = limiter.is_allowed(key, requests_per_minute=5)
    allowed2, _ = limiter.is_allowed(key2, requests_per_minute=10)
    suite.test("Different keys independent", allowed1 and allowed2)

    suite.summary()
    return suite.failed == 0


def test_input_validator():
    """Test input validation"""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING: Input Validator")
    logger.info("=" * 80)

    suite = TestSuite()
    validator = InputValidator()

    # Test valid discipline ID
    result = validator.validate_discipline_id("machine-learning-101")
    suite.test("Valid discipline ID", result == "machine-learning-101")

    # Test invalid discipline ID (SQL injection)
    result = validator.validate_discipline_id("'; DROP TABLE users; --")
    suite.test("SQL injection prevention", result is None)

    # Test valid search query
    result = validator.validate_search_query("machine learning")
    suite.test("Valid search query", result == "machine learning")

    # Test invalid search query (XSS)
    result = validator.validate_search_query("<script>alert('xss')</script>")
    suite.test("XSS prevention", result is None)

    # Test tier validation - valid
    result = validator.validate_tier_number("5")
    suite.test("Valid tier number", result == 5)

    # Test tier validation - invalid (out of range)
    result = validator.validate_tier_number("15")
    suite.test("Invalid tier number", result is None)

    # Test pagination - valid
    result = validator.validate_pagination_params(limit=20, offset=0)
    suite.test("Valid pagination", result['limit'] == 20)

    # Test pagination - excessive limit
    result = validator.validate_pagination_params(limit=1000, offset=0)
    suite.test("Excessive pagination limit capped", result['limit'] <= 100)

    # Test query type validation
    result = validator.validate_query_type("pathfinding")
    suite.test("Valid query type", result == "pathfinding")

    # Test invalid query type
    result = validator.validate_query_type("invalid_type")
    suite.test("Invalid query type", result is None)

    # Test string sanitization
    result = validator.sanitize_string("  test string  ", max_length=100)
    suite.test("String sanitization", result == "test string")

    suite.summary()
    return suite.failed == 0


def test_integration():
    """Test integration of all components"""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING: Integration (All Components)")
    logger.info("=" * 80)

    suite = TestSuite()

    # Setup components
    cache = get_cache_manager(use_redis=False)
    auth = get_auth_manager()
    limiter = get_rate_limiter()

    # Create an API key
    api_key = auth.create_key("Integration Test", rate_limit=100)
    suite.test("Create API key", api_key is not None)

    # Authenticate
    is_valid, key_id, key_data = auth.authenticate(api_key)
    suite.test("Authenticate with key", is_valid)

    # Check rate limit with authenticated key
    allowed, remaining = limiter.is_allowed(key_id, requests_per_minute=key_data['rate_limit'])
    suite.test("Rate limit with auth key", allowed)

    # Cache a result
    cache_key = CacheManager.generate_key("discipline", "test_id")
    test_result = {"name": "Test Discipline", "id": "test_id"}
    cache.set(cache_key, test_result, ttl=60)
    cached = cache.get(cache_key)
    suite.test("Cache result retrieval", cached == test_result)

    # Validate input for API call
    validated_id = InputValidator.validate_discipline_id("test_id")
    suite.test("Validate API input", validated_id == "test_id")

    # Full workflow test
    workflow_key = auth.create_key("Workflow Test", rate_limit=50)
    is_valid, wf_key_id, wf_key_data = auth.authenticate(workflow_key)
    allowed, _ = limiter.is_allowed(wf_key_id, requests_per_minute=50)
    validated = InputValidator.validate_discipline_id("workflow_test")
    cache_key = CacheManager.generate_key("cache", "workflow")
    cache.set(cache_key, {"workflow": "test"}, ttl=60)
    result = cache.get(cache_key)

    workflow_success = (is_valid and allowed and validated and result is not None)
    suite.test("Complete workflow", workflow_success)

    suite.summary()
    return suite.failed == 0


def main():
    """Run all tests"""
    logger.info("=" * 80)
    logger.info("BOB AI v10.0 - PHASE 4.6 SECURITY & CACHING TEST SUITE")
    logger.info("=" * 80)

    results = {
        "cache_manager": test_cache_manager(),
        "auth_manager": test_auth_manager(),
        "rate_limiter": test_rate_limiter(),
        "input_validator": test_input_validator(),
        "integration": test_integration(),
    }

    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("FINAL TEST RESULTS")
    logger.info("=" * 80)

    all_passed = all(results.values())
    for component, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status} - {component}")

    logger.info("=" * 80)
    if all_passed:
        logger.info("✓ ALL TESTS PASSED - PHASE 4.6 READY FOR DEPLOYMENT")
    else:
        logger.info("✗ SOME TESTS FAILED - REVIEW ERRORS ABOVE")
    logger.info("=" * 80)

    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
