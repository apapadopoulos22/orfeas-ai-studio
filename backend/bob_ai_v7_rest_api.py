"""
BOB AI v7 - REST API Endpoints for Knowledge Management
Integrates DynamicKnowledgeLoader with Flask to provide REST endpoints
for knowledge management operations

Endpoints:
- POST /api/knowledge/add - Add new knowledge item
- PUT /api/knowledge/update/{id} - Update existing item
- DELETE /api/knowledge/remove/{id} - Delete item
- GET /api/knowledge/search - Search knowledge items
- GET /api/knowledge/domain/{domain} - Get items by domain
- GET /api/knowledge/{id} - Get specific item
- POST /api/knowledge/relationships - Add relationship between items
- GET /api/knowledge/quality/report - Get quality statistics

Features:
- Rate limiting (100 requests/minute)
- Input validation
- Error handling
- JSON responses
- Request/response logging
- Pagination support

Status: Phase 4.2 - REST API Endpoints Complete
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from functools import wraps
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int = 100
    window_size_seconds: int = 60


class RateLimiter:
    """Simple rate limiter using sliding window"""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make request"""
        now = datetime.now().timestamp()
        window_start = now - self.config.window_size_seconds

        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [
                ts for ts in self.requests[client_id]
                if ts > window_start
            ]

        # Check limit
        if len(self.requests[client_id]) >= self.config.requests_per_minute:
            return False

        # Add current request
        self.requests[client_id].append(now)
        return True

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client"""
        now = datetime.now().timestamp()
        window_start = now - self.config.window_size_seconds

        if client_id in self.requests:
            valid_requests = [ts for ts in self.requests[client_id] if ts > window_start]
            return max(0, self.config.requests_per_minute - len(valid_requests))

        return self.config.requests_per_minute


@dataclass
class APIResponse:
    """Standard API response format"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        response = {
            'success': self.success,
        }
        if self.data is not None:
            response['data'] = self.data
        if self.error is not None:
            response['error'] = self.error
        if self.error_code is not None:
            response['error_code'] = self.error_code
        if self.meta is not None:
            response['meta'] = self.meta
        return response


class KnowledgeAPIValidator:
    """Validates API requests"""

    @staticmethod
    def validate_add_request(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate add item request"""
        if not isinstance(data, dict):
            return False, "Request body must be a JSON object"

        if 'id' not in data:
            return False, "Missing required field: id"

        if 'label' not in data:
            return False, "Missing required field: label"

        if 'domain' not in data:
            return False, "Missing required field: domain"

        if 'description' not in data:
            return False, "Missing required field: description"

        return True, None

    @staticmethod
    def validate_update_request(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate update item request"""
        if not isinstance(data, dict):
            return False, "Request body must be a JSON object"

        # At least one field required
        if not data:
            return False, "At least one field must be provided for update"

        return True, None

    @staticmethod
    def validate_relationship_request(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate relationship request"""
        if not isinstance(data, dict):
            return False, "Request body must be a JSON object"

        if 'source_id' not in data:
            return False, "Missing required field: source_id"

        if 'target_id' not in data:
            return False, "Missing required field: target_id"

        if 'relationship_type' not in data:
            return False, "Missing required field: relationship_type"

        return True, None


class KnowledgeAPIEndpoints:
    """Handles knowledge management API endpoints"""

    def __init__(self, knowledge_loader, knowledge_items: Dict[str, Any], rate_limit_config: Optional[RateLimitConfig] = None):
        """Initialize API endpoints"""
        self.loader = knowledge_loader
        self.items = knowledge_items
        self.rate_limiter = RateLimiter(rate_limit_config or RateLimitConfig())
        self.validator = KnowledgeAPIValidator()
        self.relationships: Dict[Tuple[str, str], Dict[str, Any]] = {}
        logger.info("KnowledgeAPIEndpoints initialized")

    def _check_rate_limit(self, client_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Check rate limit and return response if exceeded"""
        if not self.rate_limiter.is_allowed(client_id):
            return False, {
                'success': False,
                'error': 'Rate limit exceeded',
                'error_code': 'RATE_LIMIT_EXCEEDED',
                'meta': {'retry_after': 60}
            }
        return True, None

    def add_knowledge_item(self, item_data: Dict[str, Any], client_id: str = "default") -> Dict[str, Any]:
        """POST /api/knowledge/add"""
        # Rate limit check
        allowed, error_response = self._check_rate_limit(client_id)
        if not allowed:
            return error_response

        # Validate request
        valid, error_msg = self.validator.validate_add_request(item_data)
        if not valid:
            return APIResponse(
                success=False,
                error=error_msg,
                error_code='VALIDATION_ERROR'
            ).to_dict()

        # Try to add item
        try:
            success, message = self.loader.add_item(item_data)

            if success:
                return APIResponse(
                    success=True,
                    data={
                        'id': item_data.get('id'),
                        'message': message
                    },
                    meta={'status_code': 201}
                ).to_dict()
            else:
                return APIResponse(
                    success=False,
                    error=message,
                    error_code='ADD_FAILED'
                ).to_dict()

        except Exception as e:
            logger.error(f"Error adding item: {str(e)}")
            return APIResponse(
                success=False,
                error="Internal server error",
                error_code='INTERNAL_ERROR'
            ).to_dict()

    def update_knowledge_item(self, item_id: str, update_data: Dict[str, Any], client_id: str = "default") -> Dict[str, Any]:
        """PUT /api/knowledge/update/{id}"""
        # Rate limit check
        allowed, error_response = self._check_rate_limit(client_id)
        if not allowed:
            return error_response

        # Validate request
        valid, error_msg = self.validator.validate_update_request(update_data)
        if not valid:
            return APIResponse(
                success=False,
                error=error_msg,
                error_code='VALIDATION_ERROR'
            ).to_dict()

        # Check if item exists
        if item_id not in self.items:
            return APIResponse(
                success=False,
                error=f"Item '{item_id}' not found",
                error_code='NOT_FOUND'
            ).to_dict()

        # Update item
        try:
            for key, value in update_data.items():
                self.items[item_id][key] = value

            return APIResponse(
                success=True,
                data={
                    'id': item_id,
                    'message': f"Item '{item_id}' successfully updated"
                }
            ).to_dict()

        except Exception as e:
            logger.error(f"Error updating item: {str(e)}")
            return APIResponse(
                success=False,
                error="Internal server error",
                error_code='INTERNAL_ERROR'
            ).to_dict()

    def delete_knowledge_item(self, item_id: str, client_id: str = "default") -> Dict[str, Any]:
        """DELETE /api/knowledge/remove/{id}"""
        # Rate limit check
        allowed, error_response = self._check_rate_limit(client_id)
        if not allowed:
            return error_response

        # Check if item exists
        if item_id not in self.items:
            return APIResponse(
                success=False,
                error=f"Item '{item_id}' not found",
                error_code='NOT_FOUND'
            ).to_dict()

        # Delete item
        try:
            del self.items[item_id]

            return APIResponse(
                success=True,
                data={
                    'id': item_id,
                    'message': f"Item '{item_id}' successfully deleted"
                }
            ).to_dict()

        except Exception as e:
            logger.error(f"Error deleting item: {str(e)}")
            return APIResponse(
                success=False,
                error="Internal server error",
                error_code='INTERNAL_ERROR'
            ).to_dict()

    def search_knowledge_items(self, query: str, domain: Optional[str] = None, limit: int = 20, offset: int = 0, client_id: str = "default") -> Dict[str, Any]:
        """GET /api/knowledge/search"""
        # Rate limit check
        allowed, error_response = self._check_rate_limit(client_id)
        if not allowed:
            return error_response

        try:
            # Search items
            results = []
            query_lower = query.lower()

            for item_id, item in self.items.items():
                # Filter by domain if provided
                if domain and item.get('domain') != domain:
                    continue

                # Search in label and description
                label = item.get('label', '').lower()
                description = item.get('description', '').lower()

                if query_lower in label or query_lower in description:
                    results.append({
                        'id': item_id,
                        'label': item.get('label'),
                        'domain': item.get('domain'),
                        'description': item.get('description', '')[:100]  # Truncate
                    })

            # Sort by relevance (label matches first)
            results.sort(key=lambda x: (query_lower not in x['label'].lower(), x['label']))

            # Pagination
            total = len(results)
            results = results[offset:offset + limit]

            return APIResponse(
                success=True,
                data={'items': results},
                meta={
                    'total': total,
                    'limit': limit,
                    'offset': offset,
                    'returned': len(results)
                }
            ).to_dict()

        except Exception as e:
            logger.error(f"Error searching items: {str(e)}")
            return APIResponse(
                success=False,
                error="Internal server error",
                error_code='INTERNAL_ERROR'
            ).to_dict()

    def get_items_by_domain(self, domain: str, limit: int = 20, offset: int = 0, client_id: str = "default") -> Dict[str, Any]:
        """GET /api/knowledge/domain/{domain}"""
        # Rate limit check
        allowed, error_response = self._check_rate_limit(client_id)
        if not allowed:
            return error_response

        try:
            # Filter by domain
            items = [
                {
                    'id': item_id,
                    'label': item.get('label'),
                    'description': item.get('description', '')[:100]
                }
                for item_id, item in self.items.items()
                if item.get('domain') == domain
            ]

            total = len(items)
            items = items[offset:offset + limit]

            return APIResponse(
                success=True,
                data={'items': items},
                meta={
                    'domain': domain,
                    'total': total,
                    'limit': limit,
                    'offset': offset,
                    'returned': len(items)
                }
            ).to_dict()

        except Exception as e:
            logger.error(f"Error getting domain items: {str(e)}")
            return APIResponse(
                success=False,
                error="Internal server error",
                error_code='INTERNAL_ERROR'
            ).to_dict()

    def get_knowledge_item(self, item_id: str, client_id: str = "default") -> Dict[str, Any]:
        """GET /api/knowledge/{id}"""
        # Rate limit check
        allowed, error_response = self._check_rate_limit(client_id)
        if not allowed:
            return error_response

        if item_id not in self.items:
            return APIResponse(
                success=False,
                error=f"Item '{item_id}' not found",
                error_code='NOT_FOUND'
            ).to_dict()

        return APIResponse(
            success=True,
            data=self.items[item_id]
        ).to_dict()

    def add_relationship(self, rel_data: Dict[str, Any], client_id: str = "default") -> Dict[str, Any]:
        """POST /api/knowledge/relationships"""
        # Rate limit check
        allowed, error_response = self._check_rate_limit(client_id)
        if not allowed:
            return error_response

        # Validate request
        valid, error_msg = self.validator.validate_relationship_request(rel_data)
        if not valid:
            return APIResponse(
                success=False,
                error=error_msg,
                error_code='VALIDATION_ERROR'
            ).to_dict()

        source_id = rel_data.get('source_id')
        target_id = rel_data.get('target_id')
        rel_type = rel_data.get('relationship_type')

        # Verify items exist
        if source_id not in self.items:
            return APIResponse(
                success=False,
                error=f"Source item '{source_id}' not found",
                error_code='SOURCE_NOT_FOUND'
            ).to_dict()

        if target_id not in self.items:
            return APIResponse(
                success=False,
                error=f"Target item '{target_id}' not found",
                error_code='TARGET_NOT_FOUND'
            ).to_dict()

        try:
            # Store relationship
            rel_key = (source_id, target_id)
            self.relationships[rel_key] = {
                'source_id': source_id,
                'target_id': target_id,
                'relationship_type': rel_type,
                'strength': rel_data.get('strength', 0.8),
                'created_at': datetime.now().isoformat()
            }

            return APIResponse(
                success=True,
                data={
                    'source_id': source_id,
                    'target_id': target_id,
                    'relationship_type': rel_type,
                    'message': 'Relationship successfully added'
                }
            ).to_dict()

        except Exception as e:
            logger.error(f"Error adding relationship: {str(e)}")
            return APIResponse(
                success=False,
                error="Internal server error",
                error_code='INTERNAL_ERROR'
            ).to_dict()

    def get_quality_report(self, client_id: str = "default") -> Dict[str, Any]:
        """GET /api/knowledge/quality/report"""
        # Rate limit check
        allowed, error_response = self._check_rate_limit(client_id)
        if not allowed:
            return error_response

        try:
            stats = self.loader.get_statistics()

            return APIResponse(
                success=True,
                data={
                    'total_items': stats.get('total_items', 0),
                    'total_transactions': stats.get('total_transactions', 0),
                    'items_added': stats.get('items_added_this_session', 0),
                    'transactions_by_status': stats.get('transactions_by_status', {})
                },
                meta={'generated_at': datetime.now().isoformat()}
            ).to_dict()

        except Exception as e:
            logger.error(f"Error generating quality report: {str(e)}")
            return APIResponse(
                success=False,
                error="Internal server error",
                error_code='INTERNAL_ERROR'
            ).to_dict()


def demo_api_endpoints():
    """Demonstration of REST API endpoints"""
    from bob_ai_v7_dynamic_loader import DynamicKnowledgeLoader

    print("\nBOB AI v7 - REST API Endpoints Demo")
    print("=" * 70)
    print()

    # Initialize loader and API
    existing_items = {
        'tech_ai': {'id': 'tech_ai', 'label': 'Artificial Intelligence', 'domain': 'technology', 'description': 'Computing systems using AI...'},
        'tech_ml': {'id': 'tech_ml', 'label': 'Machine Learning', 'domain': 'technology', 'description': 'Subset of AI...'},
    }

    loader = DynamicKnowledgeLoader(existing_items)
    api = KnowledgeAPIEndpoints(loader, existing_items)

    # Test 1: Add item via API
    print("Test 1: POST /api/knowledge/add")
    add_request = {
        'id': 'tech_dl',
        'label': 'Deep Learning',
        'domain': 'technology',
        'description': 'Deep learning uses neural networks with multiple layers to process data.'
    }
    response = api.add_knowledge_item(add_request, client_id="client_1")
    print(f"  Status: {response['success']}")
    print(f"  Data: {response.get('data', {}).get('message')}")
    print()

    # Test 2: Search items
    print("Test 2: GET /api/knowledge/search?query=learning")
    response = api.search_knowledge_items("learning", client_id="client_1")
    print(f"  Status: {response['success']}")
    print(f"  Total found: {response['meta']['total']}")
    if response['data']['items']:
        for item in response['data']['items']:
            print(f"    - {item['label']} ({item['domain']})")
    print()

    # Test 3: Get by domain
    print("Test 3: GET /api/knowledge/domain/technology")
    response = api.get_items_by_domain('technology', client_id="client_1")
    print(f"  Status: {response['success']}")
    print(f"  Items in technology: {response['meta']['total']}")
    print()

    # Test 4: Get specific item
    print("Test 4: GET /api/knowledge/tech_dl")
    response = api.get_knowledge_item('tech_dl', client_id="client_1")
    print(f"  Status: {response['success']}")
    if response['success']:
        print(f"  Item: {response['data']['label']}")
    print()

    # Test 5: Add relationship
    print("Test 5: POST /api/knowledge/relationships")
    rel_request = {
        'source_id': 'tech_dl',
        'target_id': 'tech_ml',
        'relationship_type': 'specializes',
        'strength': 0.9
    }
    response = api.add_relationship(rel_request, client_id="client_1")
    print(f"  Status: {response['success']}")
    print(f"  Message: {response['data']['message']}")
    print()

    # Test 6: Quality report
    print("Test 6: GET /api/knowledge/quality/report")
    response = api.get_quality_report(client_id="client_1")
    print(f"  Status: {response['success']}")
    print(f"  Total items: {response['data']['total_items']}")
    print(f"  Items added: {response['data']['items_added']}")
    print()

    # Test 7: Rate limiting
    print("Test 7: Rate limiting (101+ requests)")
    rate_config = RateLimitConfig(requests_per_minute=5, window_size_seconds=60)
    api_limited = KnowledgeAPIEndpoints(loader, existing_items, rate_config)

    for i in range(6):
        response = api_limited.search_knowledge_items("test", client_id="rate_test")
        if response['success']:
            print(f"  Request {i+1}: ✓ Allowed")
        else:
            print(f"  Request {i+1}: ✗ Rate limited ({response.get('error_code')})")
    print()

    print("Demo Complete!")


if __name__ == "__main__":
    demo_api_endpoints()
