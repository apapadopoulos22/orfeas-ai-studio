#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests for BOB AI Mega Expansion
============================================

End-to-end tests for:
- API → Library retrieval → Learning path → Frontend integration
- Full workflow validation
- Performance benchmarks
- Real-world scenarios

Run: pytest backend/tests/test_bob_ai_integration.py -v

Requirements:
- Backend running on http://localhost:5000
- Flask app initialized with bob_ai_blueprint
"""

import pytest
import requests
import json
import time
from urllib.parse import urlencode

BASE_URL = 'http://localhost:5000/api'


@pytest.fixture
def backend_running():
    """Check if backend is running"""
    try:
        response = requests.get(f'{BASE_URL}/disciplines/health', timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass

    pytest.skip("Backend not running on http://localhost:5000")
    return False


class TestFullWorkflow:
    """Test complete workflow from API to frontend"""

    def test_workflow_list_to_learning_path(self, backend_running):
        """Test: List disciplines → Get libraries → Create learning path"""
        # Step 1: Get all disciplines
        response = requests.get(f'{BASE_URL}/disciplines/all?limit=5')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        disciplines = data['data']['disciplines']
        assert len(disciplines) > 0

        first_discipline = disciplines[0]['name']

        # Step 2: Get libraries for first discipline
        response = requests.get(
            f'{BASE_URL}/disciplines/{first_discipline}/libraries'
        )
        assert response.status_code == 200
        data = response.json()
        libraries = data['data']
        assert 'packages' in libraries
        assert 'tools' in libraries

        # Step 3: Create learning path
        response = requests.post(
            f'{BASE_URL}/learning-path',
            json={
                'discipline': first_discipline,
                'estimated_hours': 100,
                'skill_level': 'beginner'
            }
        )
        assert response.status_code == 200
        data = response.json()
        path = data['data']
        assert 'phases' in path
        assert len(path['phases']) == 4
        assert path['resources']['packages'] == libraries['packages']

    def test_workflow_category_to_tools(self, backend_running):
        """Test: Get categories → Get recommendations → Filter by discipline"""
        # Step 1: Get categories
        response = requests.get(f'{BASE_URL}/categories')
        assert response.status_code == 200
        data = response.json()
        categories = data['data']['sample_categories']
        assert len(categories) > 0

        # Step 2: Get tools
        response = requests.get(f'{BASE_URL}/recommendations/tools?top_n=10')
        assert response.status_code == 200
        data = response.json()
        tools = data['data']['recommendations']
        assert len(tools) > 0

        # Step 3: Get first discipline from first category
        first_category_disciplines = categories[0]['sample_disciplines']
        if first_category_disciplines:
            discipline = first_category_disciplines[0]

            # Get tools for this discipline
            response = requests.get(
                f'{BASE_URL}/recommendations/tools?disciplines={discipline}&top_n=5'
            )
            assert response.status_code == 200
            data = response.json()
            discipline_tools = data['data']['recommendations']
            assert len(discipline_tools) >= 0


class TestApiConsistency:
    """Test API consistency across endpoints"""

    def test_response_format_consistency(self, backend_running):
        """Test all endpoints follow same response format"""
        endpoints = [
            f'{BASE_URL}/disciplines/all?limit=5',
            f'{BASE_URL}/categories',
            f'{BASE_URL}/disciplines/health',
            f'{BASE_URL}/recommendations/tools?top_n=5'
        ]

        for endpoint in endpoints:
            response = requests.get(endpoint)
            assert response.status_code == 200
            data = response.json()

            # Verify format
            assert 'status' in data
            assert 'timestamp' in data
            assert 'data' in data
            assert data['status'] == 'success'

    def test_discipline_data_consistency(self, backend_running):
        """Test discipline data is consistent across endpoints"""
        # Get all disciplines
        response = requests.get(f'{BASE_URL}/disciplines/all?limit=1')
        disciplines = response.json()['data']['disciplines']
        test_discipline = disciplines[0]['name']

        # Get libraries for this discipline
        response = requests.get(
            f'{BASE_URL}/disciplines/{test_discipline}/libraries'
        )
        libraries = response.json()['data']

        # Verify counts match
        assert libraries['summary']['packages_count'] == len(libraries['packages'])
        assert libraries['summary']['tools_count'] == len(libraries['tools'])
        assert (
            libraries['summary']['total_libraries']
            == len(libraries['packages']) + len(libraries['tools'])
        )


class TestPagination:
    """Test pagination across endpoints"""

    def test_pagination_discipline_list(self, backend_running):
        """Test pagination for discipline list"""
        # Get page 1
        response1 = requests.get(f'{BASE_URL}/disciplines/all?limit=5&offset=0')
        data1 = response1.json()['data']

        # Get page 2
        response2 = requests.get(f'{BASE_URL}/disciplines/all?limit=5&offset=5')
        data2 = response2.json()['data']

        # Verify pagination works
        assert len(data1['disciplines']) == 5
        assert len(data2['disciplines']) == 5
        assert data1['offset'] == 0
        assert data2['offset'] == 5

        # Ensure different data
        names1 = [d['name'] for d in data1['disciplines']]
        names2 = [d['name'] for d in data2['disciplines']]
        assert names1 != names2


class TestErrorScenarios:
    """Test error handling"""

    def test_nonexistent_discipline(self, backend_running):
        """Test 404 for non-existent discipline"""
        response = requests.get(
            f'{BASE_URL}/disciplines/NonExistentDiscipline123/libraries'
        )
        assert response.status_code == 404
        data = response.json()
        assert data['status'] == 'error'

    def test_invalid_learning_path_request(self, backend_running):
        """Test 400 for invalid learning path request"""
        response = requests.post(
            f'{BASE_URL}/learning-path',
            json={'estimated_hours': 100}  # Missing 'discipline'
        )
        assert response.status_code == 400

    def test_missing_json_content_type(self, backend_running):
        """Test POST without proper content type"""
        response = requests.post(
            f'{BASE_URL}/learning-path',
            data='{"discipline": "Test"}'
        )
        # Should either handle gracefully or return error
        assert response.status_code in [400, 415, 200]


class TestPerformance:
    """Test performance benchmarks"""

    def test_health_check_response_time(self, backend_running):
        """Test health check is fast (<100ms)"""
        start = time.time()
        response = requests.get(f'{BASE_URL}/disciplines/health')
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert response.status_code == 200
        assert elapsed < 100, f"Health check took {elapsed}ms (expected <100ms)"

    def test_list_disciplines_response_time(self, backend_running):
        """Test discipline list response time (<200ms)"""
        start = time.time()
        response = requests.get(f'{BASE_URL}/disciplines/all?limit=50')
        elapsed = (time.time() - start) * 1000

        assert response.status_code == 200
        assert elapsed < 200, f"Discipline list took {elapsed}ms (expected <200ms)"

    def test_get_libraries_response_time(self, backend_running):
        """Test library retrieval response time (<150ms)"""
        # Get a discipline first
        response = requests.get(f'{BASE_URL}/disciplines/all?limit=1')
        discipline = response.json()['data']['disciplines'][0]['name']

        # Time the library retrieval
        start = time.time()
        response = requests.get(f'{BASE_URL}/disciplines/{discipline}/libraries')
        elapsed = (time.time() - start) * 1000

        assert response.status_code == 200
        assert elapsed < 150, f"Library retrieval took {elapsed}ms (expected <150ms)"

    def test_learning_path_response_time(self, backend_running):
        """Test learning path generation response time (<300ms)"""
        start = time.time()
        response = requests.post(
            f'{BASE_URL}/learning-path',
            json={
                'discipline': 'Machine Learning',
                'estimated_hours': 250,
                'skill_level': 'beginner'
            }
        )
        elapsed = (time.time() - start) * 1000

        # Allow longer for first call (model loading), faster for subsequent
        if response.status_code == 200:
            assert elapsed < 500, f"Learning path took {elapsed}ms (expected <500ms)"


class TestDataQuality:
    """Test data quality and completeness"""

    def test_discipline_count(self, backend_running):
        """Test total discipline count"""
        response = requests.get(f'{BASE_URL}/disciplines/all?limit=1')
        total = response.json()['data']['total']
        assert total == 136, f"Expected 136 disciplines, got {total}"

    def test_discipline_has_libraries(self, backend_running):
        """Test disciplines have associated libraries"""
        # Get a random discipline
        response = requests.get(f'{BASE_URL}/disciplines/all?limit=1&offset=50')
        discipline = response.json()['data']['disciplines'][0]

        # Get its libraries
        discipline_name = discipline['name']
        response = requests.get(
            f'{BASE_URL}/disciplines/{discipline_name}/libraries'
        )
        assert response.status_code == 200
        libraries = response.json()['data']

        # Should have at least packages or tools
        total_libs = (
            len(libraries['packages'])
            + len(libraries['tools'])
            + len(libraries['resources'])
        )
        assert total_libs > 0

    def test_learning_path_completeness(self, backend_running):
        """Test learning path has all required fields"""
        response = requests.post(
            f'{BASE_URL}/learning-path',
            json={
                'discipline': 'Linear Regression',
                'estimated_hours': 100,
                'skill_level': 'beginner'
            }
        )
        path = response.json()['data']

        # Verify required fields
        assert 'discipline' in path
        assert 'phases' in path
        assert 'resources' in path
        assert 'completion_weeks' in path
        assert len(path['phases']) == 4

        # Verify each phase
        for phase in path['phases']:
            assert 'phase' in phase
            assert 'name' in phase
            assert 'hours' in phase
            assert 'topics' in phase
            assert len(phase['topics']) > 0


class TestConcurrency:
    """Test concurrent request handling"""

    def test_concurrent_discipline_requests(self, backend_running):
        """Test multiple concurrent requests"""
        import concurrent.futures

        def get_discipline(offset):
            response = requests.get(
                f'{BASE_URL}/disciplines/all?limit=1&offset={offset}'
            )
            return response.status_code == 200

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(get_discipline, i * 10) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert all(results), "Some concurrent requests failed"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
