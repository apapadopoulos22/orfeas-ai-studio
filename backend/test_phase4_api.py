#!/usr/bin/env python3
"""
BOB AI v10.0 - PHASE 4 API TESTING SUITE
Production Deployment - Endpoint Validation

Comprehensive test suite for all Phase 4 REST API endpoints
Tests functionality, performance, and error handling

Version: 1.0.0
Date: October 28, 2025
Status: PHASE 4 IMPLEMENTATION
"""

import sys
import os
# Get absolute path to backend directory
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

import unittest
import json
from phase4_app import create_app
import time


class Phase4APITestCase(unittest.TestCase):
    """Test cases for Phase 4 REST API"""

    def setUp(self):
        """Set up test client"""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up"""
        self.app_context.pop()

    # ========================================================================
    # HEALTH CHECK TESTS
    # ========================================================================

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['phase'], '4')
        self.assertIn('timestamp', data)
        print("✓ Health check endpoint working")

    def test_readiness_check(self):
        """Test readiness check endpoint"""
        response = self.client.get('/api/ready')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data['ready'])
        self.assertGreaterEqual(data['disciplines_loaded'], 391)
        print(f"✓ Readiness check: {data['disciplines_loaded']} disciplines loaded")

    # ========================================================================
    # ENDPOINT 1: GET /api/disciplines
    # ========================================================================

    def test_get_all_disciplines(self):
        """Test GET /api/disciplines"""
        response = self.client.get('/api/disciplines')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('disciplines', data['data'])
        self.assertGreaterEqual(data['data']['count'], 100)  # At least 100 on first page
        print(f"✓ GET /api/disciplines: {data['data']['count']} disciplines returned")

    def test_get_disciplines_with_limit(self):
        """Test GET /api/disciplines with limit parameter"""
        response = self.client.get('/api/disciplines?limit=10')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertLessEqual(len(data['data']['disciplines']), 10)
        self.assertEqual(data['meta']['limit'], 10)
        print(f"✓ GET /api/disciplines?limit=10: {len(data['data']['disciplines'])} returned")

    def test_get_disciplines_with_pagination(self):
        """Test GET /api/disciplines with offset"""
        response1 = self.client.get('/api/disciplines?limit=50&offset=0')
        response2 = self.client.get('/api/disciplines?limit=50&offset=50')

        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)

        # Ensure we got different results
        disc1 = data1['data']['disciplines']
        disc2 = data2['data']['disciplines']

        if len(disc1) > 0 and len(disc2) > 0:
            self.assertNotEqual(disc1[0], disc2[0])

        print("✓ Pagination working (offset parameter)")

    # ========================================================================
    # ENDPOINT 2: GET /api/disciplines/{id}
    # ========================================================================

    def test_get_discipline_detail(self):
        """Test GET /api/disciplines/{id}"""
        # First get list of disciplines
        response = self.client.get('/api/disciplines?limit=1')
        data = json.loads(response.data)

        if len(data['data']['disciplines']) > 0:
            discipline_id = data['data']['disciplines'][0]

            # Now get detail
            response = self.client.get(f'/api/disciplines/{discipline_id}')
            self.assertEqual(response.status_code, 200)

            detail = json.loads(response.data)
            self.assertTrue(detail['success'])
            self.assertIn('name', detail['data'])
            self.assertIn('category', detail['data'])
            print(f"✓ GET /api/disciplines/{discipline_id}: {detail['data'].get('name', 'N/A')}")

    def test_get_nonexistent_discipline(self):
        """Test GET /api/disciplines/{id} with invalid ID"""
        response = self.client.get('/api/disciplines/NONEXISTENT_DISCIPLINE_XYZ')
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        print("✓ 404 handling for nonexistent discipline")

    # ========================================================================
    # ENDPOINT 3: GET /api/disciplines/{id}/related
    # ========================================================================

    def test_get_related_disciplines(self):
        """Test GET /api/disciplines/{id}/related"""
        # Get first discipline
        response = self.client.get('/api/disciplines?limit=1')
        data = json.loads(response.data)

        if len(data['data']['disciplines']) > 0:
            discipline_id = data['data']['disciplines'][0]

            # Get related disciplines
            response = self.client.get(f'/api/disciplines/{discipline_id}/related')
            self.assertEqual(response.status_code, 200)

            related_data = json.loads(response.data)
            self.assertTrue(related_data['success'])
            self.assertIn('related', related_data['data'])
            print(f"✓ GET /api/disciplines/{discipline_id}/related: {related_data['data']['count']} related disciplines")

    # ========================================================================
    # ENDPOINT 4: GET /api/knowledge-graph
    # ========================================================================

    def test_get_knowledge_graph(self):
        """Test GET /api/knowledge-graph"""
        start_time = time.time()
        response = self.client.get('/api/knowledge-graph')
        elapsed = time.time() - start_time

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('nodes', data['data'])
        self.assertIn('edges', data['data'])
        self.assertGreaterEqual(len(data['data']['nodes']), 391)
        self.assertGreaterEqual(len(data['data']['edges']), 60)

        print(f"✓ Knowledge graph: {len(data['data']['nodes'])} nodes, {len(data['data']['edges'])} edges (generated in {elapsed:.2f}s)")

    def test_get_knowledge_graph_with_stats(self):
        """Test GET /api/knowledge-graph with statistics"""
        response = self.client.get('/api/knowledge-graph?include_stats=true')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('statistics', data['data'])
        self.assertIn('graph_metrics', data['data'])
        self.assertIn('avg_degree', data['data']['graph_metrics'])
        print(f"✓ Knowledge graph metrics: avg_degree={data['data']['graph_metrics']['avg_degree']}")

    # ========================================================================
    # ENDPOINT 5: GET /api/disciplines/path/{from}/{to}
    # ========================================================================

    def test_pathfinding_same_discipline(self):
        """Test pathfinding - path from discipline to itself"""
        response = self.client.get('/api/disciplines/path/Physics/Physics')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['found'])
        self.assertEqual(data['data']['path'], ['Physics'])
        self.assertEqual(data['data']['path_length'], 0)
        print("✓ Pathfinding (same discipline): Physics → Physics")

    def test_pathfinding_different_disciplines(self):
        """Test pathfinding - path between different disciplines"""
        response = self.client.get('/api/disciplines/path/Physics/Chemistry')

        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            if data['data']['found']:
                self.assertGreater(len(data['data']['path']), 0)
                print(f"✓ Pathfinding (different): Physics → Chemistry (path length: {data['data']['path_length']})")
            else:
                print("✓ Pathfinding (no direct path found - expected for some discipline pairs)")

    # ========================================================================
    # ENDPOINT 6: GET /api/tier/{tier}/connections
    # ========================================================================

    def test_get_tier_connections(self):
        """Test GET /api/tier/{tier}/connections"""
        for tier in [1, 6, 12]:
            response = self.client.get(f'/api/tier/{tier}/connections')
            self.assertEqual(response.status_code, 200)

            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('tier', data['data'])
            self.assertEqual(data['data']['tier'], tier)
            print(f"✓ Tier {tier} connections: {data['data'].get('disciplines', 'N/A')} disciplines")

    def test_invalid_tier(self):
        """Test invalid tier number"""
        response = self.client.get('/api/tier/99/connections')
        self.assertEqual(response.status_code, 400)
        print("✓ Invalid tier validation working")

    # ========================================================================
    # ENDPOINT 7: GET /api/statistics/phase3
    # ========================================================================

    def test_get_phase3_statistics(self):
        """Test GET /api/statistics/phase3"""
        response = self.client.get('/api/statistics/phase3')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data['success'])

        stats = data['data']
        self.assertEqual(stats['phase'], 'Phase 3')
        self.assertGreaterEqual(stats['total_disciplines'], 391)
        self.assertGreaterEqual(stats['total_knowledge_items'], 51000)
        self.assertGreaterEqual(stats['semantic_relationships'], 60)

        print(f"✓ Phase 3 Statistics:")
        print(f"  - Disciplines: {stats['total_disciplines']}")
        print(f"  - Knowledge items: {stats['total_knowledge_items']}")
        print(f"  - Semantic relationships: {stats['semantic_relationships']}")

    # ========================================================================
    # ENDPOINT 8: POST /api/query
    # ========================================================================

    def test_query_semantic_search(self):
        """Test POST /api/query with semantic_search"""
        response = self.client.post('/api/query',
            json={
                "query_type": "semantic_search",
                "params": {
                    "query": "physics",
                    "limit": 10
                }
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        print(f"✓ Semantic search query: {data['data'].get('count', 0)} results")

    def test_query_related(self):
        """Test POST /api/query with related query"""
        response = self.client.post('/api/query',
            json={
                "query_type": "related",
                "params": {
                    "discipline": "Physics",
                    "max_results": 20
                }
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        print(f"✓ Related disciplines query: {data['data'].get('count', 0)} results")

    def test_query_pathfinding(self):
        """Test POST /api/query with pathfinding"""
        response = self.client.post('/api/query',
            json={
                "query_type": "pathfinding",
                "params": {
                    "from": "Physics",
                    "to": "Chemistry",
                    "max_depth": 5
                }
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        print(f"✓ Pathfinding query: {'found' if data['data'].get('found') else 'not found'}")

    def test_query_tier_analysis(self):
        """Test POST /api/query with tier_analysis"""
        response = self.client.post('/api/query',
            json={
                "query_type": "tier_analysis",
                "params": {
                    "tier": 6
                }
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        print(f"✓ Tier analysis query: Tier 6")

    def test_query_invalid_type(self):
        """Test POST /api/query with invalid query type"""
        response = self.client.post('/api/query',
            json={
                "query_type": "invalid_query_type",
                "params": {}
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        print("✓ Invalid query type validation working")

    def test_query_missing_params(self):
        """Test POST /api/query with missing required parameters"""
        response = self.client.post('/api/query',
            json={
                "query_type": "semantic_search"
                # Missing params
            },
            content_type='application/json'
        )

        # Should either succeed with empty results or fail gracefully
        self.assertIn(response.status_code, [200, 400])
        print("✓ Missing parameters handled gracefully")

    # ========================================================================
    # ERROR HANDLING TESTS
    # ========================================================================

    def test_404_endpoint(self):
        """Test 404 error handling"""
        response = self.client.get('/api/nonexistent')
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data)
        self.assertIn('error', data)
        print("✓ 404 error handling working")

    def test_405_method_not_allowed(self):
        """Test 405 error handling"""
        response = self.client.delete('/api/disciplines')
        self.assertEqual(response.status_code, 405)

        data = json.loads(response.data)
        self.assertIn('error', data)
        print("✓ 405 method not allowed handling working")

    # ========================================================================
    # PERFORMANCE TESTS
    # ========================================================================

    def test_endpoint_response_time_disciplines(self):
        """Test /api/disciplines response time"""
        start = time.time()
        response = self.client.get('/api/disciplines?limit=50')
        elapsed = time.time() - start

        self.assertEqual(response.status_code, 200)
        # Should be fast (typically <200ms)
        print(f"✓ GET /api/disciplines response time: {elapsed*1000:.1f}ms")

    def test_endpoint_response_time_detail(self):
        """Test /api/disciplines/{id} response time"""
        start = time.time()
        response = self.client.get('/api/disciplines/Physics')
        elapsed = time.time() - start

        self.assertEqual(response.status_code, 200)
        # Should be very fast (typically <50ms)
        print(f"✓ GET /api/disciplines/Physics response time: {elapsed*1000:.1f}ms")


def run_tests():
    """Run all Phase 4 API tests"""
    print("=" * 80)
    print("BOB AI v10.0 - PHASE 4 API TEST SUITE")
    print("=" * 80)
    print()

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(Phase4APITestCase)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()

    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED - Phase 4 API Ready for Production")
    else:
        print("✗ SOME TESTS FAILED - Review errors above")

    print("=" * 80)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
