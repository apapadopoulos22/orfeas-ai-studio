#!/usr/bin/env python3
"""
BOB AI v10.0 - PHASE 4.6 INPUT VALIDATOR
Request Input Validation & Sanitization

Validates and sanitizes all API input parameters
Prevents injection attacks and malformed data

Version: 1.0.0
Date: October 28, 2025
Status: PHASE 4.6 IMPLEMENTATION
"""

import logging
import re
from typing import Any, Optional, Dict, List
from urllib.parse import quote, unquote

logger = logging.getLogger(__name__)


class InputValidator:
    """Validates and sanitizes API input"""

    # Allowed characters for different field types
    DISCIPLINE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_\.&\'()]+$')
    QUERY_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_\.&\'(),;:?!]+$')
    TIER_PATTERN = re.compile(r'^[0-9]{1,2}$')
    PAGINATION_PATTERN = re.compile(r'^[0-9]+$')

    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bOR\b.*=|'.*'|\".*\")",
        r"(;|--|/\*|\*/|UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE)",
        r"(xp_|sp_|exec|execute)"
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"(<script|javascript:|onerror=|onclick=|<iframe|<object)",
        r"(&#|&#x|&#X|%|eval\(|expression\()"
    ]

    @staticmethod
    def validate_discipline_id(discipline_id: Any, max_length: int = 100) -> Optional[str]:
        """Validate discipline ID"""
        if not isinstance(discipline_id, str):
            logger.warning(f"Invalid discipline ID type: {type(discipline_id)}")
            return None

        # Check length
        if len(discipline_id) > max_length:
            logger.warning(f"Discipline ID too long: {len(discipline_id)}")
            return None

        # Check for dangerous patterns
        if InputValidator._has_injection_pattern(discipline_id):
            logger.warning(f"Potential injection in discipline ID: {discipline_id}")
            return None

        # Sanitize
        return discipline_id.strip()

    @staticmethod
    def validate_search_query(query: Any, max_length: int = 200) -> Optional[str]:
        """Validate search query"""
        if not isinstance(query, str):
            logger.warning(f"Invalid search query type: {type(query)}")
            return None

        # Check length
        if len(query) > max_length:
            logger.warning(f"Search query too long: {len(query)}")
            return None

        # Check for dangerous patterns
        if InputValidator._has_injection_pattern(query):
            logger.warning(f"Potential injection in search query: {query}")
            return None

        # Allow only safe characters
        if not InputValidator.QUERY_PATTERN.match(query):
            logger.warning(f"Search query contains invalid characters: {query}")
            return None

        # Sanitize
        return query.strip()

    @staticmethod
    def validate_tier_number(tier: Any) -> Optional[int]:
        """Validate tier number (1-12)"""
        if isinstance(tier, str):
            if not tier.isdigit():
                logger.warning(f"Invalid tier format: {tier}")
                return None
            tier = int(tier)

        if not isinstance(tier, int):
            logger.warning(f"Invalid tier type: {type(tier)}")
            return None

        if tier < 1 or tier > 12:
            logger.warning(f"Tier out of range: {tier}")
            return None

        return tier

    @staticmethod
    def validate_pagination_params(
        limit: Any = 20,
        offset: Any = 0,
        max_limit: int = 100
    ) -> Optional[Dict[str, int]]:
        """Validate pagination parameters"""
        try:
            # Validate limit
            if isinstance(limit, str):
                if not limit.isdigit():
                    logger.warning(f"Invalid limit format: {limit}")
                    return None
                limit = int(limit)

            if not isinstance(limit, int):
                logger.warning(f"Invalid limit type: {type(limit)}")
                return None

            if limit < 1 or limit > max_limit:
                logger.warning(f"Limit out of range: {limit}")
                limit = min(max_limit, max(1, limit))

            # Validate offset
            if isinstance(offset, str):
                if not offset.isdigit():
                    logger.warning(f"Invalid offset format: {offset}")
                    return None
                offset = int(offset)

            if not isinstance(offset, int):
                logger.warning(f"Invalid offset type: {type(offset)}")
                return None

            if offset < 0:
                logger.warning(f"Negative offset: {offset}")
                offset = 0

            return {'limit': limit, 'offset': offset}

        except Exception as e:
            logger.error(f"Pagination validation error: {e}")
            return None

    @staticmethod
    def validate_query_type(query_type: Any) -> Optional[str]:
        """Validate query type"""
        allowed_types = ['pathfinding', 'related', 'semantic_search', 'tier_analysis']

        if not isinstance(query_type, str):
            logger.warning(f"Invalid query type: {type(query_type)}")
            return None

        query_type = query_type.lower().strip()

        if query_type not in allowed_types:
            logger.warning(f"Unsupported query type: {query_type}")
            return None

        return query_type

    @staticmethod
    def validate_query_params(query_type: str, params: Dict) -> Optional[Dict]:
        """Validate query parameters based on query type"""
        if query_type == 'pathfinding':
            if 'from_id' not in params or 'to_id' not in params:
                logger.warning("Missing pathfinding parameters")
                return None

            from_id = InputValidator.validate_discipline_id(params['from_id'])
            to_id = InputValidator.validate_discipline_id(params['to_id'])

            if not from_id or not to_id:
                return None

            return {'from_id': from_id, 'to_id': to_id}

        elif query_type == 'related':
            if 'discipline_id' not in params:
                logger.warning("Missing discipline_id parameter")
                return None

            discipline_id = InputValidator.validate_discipline_id(params['discipline_id'])
            if not discipline_id:
                return None

            return {'discipline_id': discipline_id}

        elif query_type == 'semantic_search':
            if 'query' not in params:
                logger.warning("Missing query parameter")
                return None

            query = InputValidator.validate_search_query(params['query'])
            if not query:
                return None

            return {'query': query}

        elif query_type == 'tier_analysis':
            if 'tier' not in params:
                logger.warning("Missing tier parameter")
                return None

            tier = InputValidator.validate_tier_number(params['tier'])
            if tier is None:
                return None

            return {'tier': tier}

        return None

    @staticmethod
    def _has_injection_pattern(text: str) -> bool:
        """Check if text has potential injection patterns"""
        text_upper = text.upper()

        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_upper, re.IGNORECASE):
                logger.debug(f"Detected injection pattern: {pattern}")
                return True

        for pattern in InputValidator.XSS_PATTERNS:
            if re.search(pattern, text_upper, re.IGNORECASE):
                logger.debug(f"Detected XSS pattern: {pattern}")
                return True

        return False

    @staticmethod
    def sanitize_string(value: str, max_length: int = 500) -> str:
        """Sanitize string value"""
        if not isinstance(value, str):
            return ""

        # Remove null bytes
        value = value.replace('\x00', '')

        # Truncate to max length
        value = value[:max_length]

        # Remove control characters
        value = ''.join(c for c in value if ord(c) >= 32 or c in '\t\n\r')

        return value.strip()


class ValidationException(Exception):
    """Exception raised when validation fails"""

    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"Validation failed for {field}: {reason}")


def validate_input(field_name: str, value: Any, field_type: str = 'string') -> Optional[Any]:
    """
    Quick validation function

    Args:
        field_name: Name of field being validated
        value: Value to validate
        field_type: Type of field ('discipline_id', 'search_query', 'tier', 'pagination', etc.)

    Returns:
        Validated value or None if invalid
    """
    try:
        if field_type == 'discipline_id':
            return InputValidator.validate_discipline_id(value)
        elif field_type == 'search_query':
            return InputValidator.validate_search_query(value)
        elif field_type == 'tier':
            return InputValidator.validate_tier_number(value)
        elif field_type == 'pagination':
            return InputValidator.validate_pagination_params()
        else:
            return InputValidator.sanitize_string(value)
    except Exception as e:
        logger.error(f"Validation error for {field_name}: {e}")
        raise ValidationException(field_name, str(e))


if __name__ == '__main__':
    # Test input validator
    logging.basicConfig(level=logging.INFO)

    validator = InputValidator()

    # Test cases
    test_cases = [
        ("Valid discipline", "machine-learning-101", validator.validate_discipline_id),
        ("SQL injection attempt", "'; DROP TABLE users; --", validator.validate_discipline_id),
        ("Valid search", "machine learning", validator.validate_search_query),
        ("Valid tier", "5", validator.validate_tier_number),
        ("Invalid tier", "15", validator.validate_tier_number),
        ("Pagination", (20, 0), lambda x: validator.validate_pagination_params(x[0], x[1])),
    ]

    for test_name, test_value, validator_func in test_cases:
        result = validator_func(test_value)
        status = "✓" if result is not None else "✗"
        print(f"{status} {test_name}: {result}")
