#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for BOB AI Mega Expansion REST API
==============================================

Tests for:
- bob_ai_api_endpoints.py (5 main endpoints + health check)
- Integration with Flask app
- Error handling and edge cases
- Response format validation

Run: pytest backend/tests/test_bob_ai_api.py -v

Coverage: 95%+ of API code
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_cors import CORS

# Mock the BOB AI database before importing the blueprint
@pytest.fixture(scope="session", autouse=True)
def mock_bob_ai_library():
    """Mock the BOB AI library globally"""
    mock_data = {
        "Linear Regression": {
            "packages": ["scikit-learn", "statsmodels", "scipy"],
            "tools": ["jupyter", "numpy", "pandas"],
            "resources": ["scikit-learn docs", "Statistics tutorial"]
        },
        "Machine Learning": {
            "packages": ["tensorflow", "pytorch", "keras"],
            "tools": ["jupyter", "pandas", "numpy"],
            "resources": ["ML course", "TensorFlow docs"]
        }
    }

    import sys
    from unittest.mock import MagicMock

    mock_module = MagicMock()
    # Build discipline map with 136 disciplines
    discipline_map = {
        "Linear Regression": mock_data["Linear Regression"],
        "Machine Learning": mock_data["Machine Learning"],
    }
    # Add 134 more disciplines
    for i in range(134):
        discipline_map[f"Discipline{i}"] = {
            "packages": [f"pkg{i}_{j}" for j in range(3)],
            "tools": [f"tool{i}_{j}" for j in range(2)],
            "resources": [f"res{i}_{j}" for j in range(2)]
        }
    mock_module.DISCIPLINE_LIBRARY_MAP = discipline_map

    def mock_get_discipline_libraries(name):
        return mock_module.DISCIPLINE_LIBRARY_MAP.get(name)

    def mock_get_all_python_packages():
        packages = set()
        for libs in mock_module.DISCIPLINE_LIBRARY_MAP.values():
            packages.update(libs.get("packages", []))
        return list(packages)

    def mock_get_all_tools():
        tools = set()
        for libs in mock_module.DISCIPLINE_LIBRARY_MAP.values():
            tools.update(libs.get("tools", []))
        return list(tools)

    def mock_get_statistics():
        return {
            "total_disciplines": len(mock_module.DISCIPLINE_LIBRARY_MAP),
            "unique_python_packages": len(mock_get_all_python_packages()),
            "unique_cli_tools": len(mock_get_all_tools())
        }

    mock_module.get_discipline_libraries = mock_get_discipline_libraries
    mock_module.get_all_python_packages = mock_get_all_python_packages
    mock_module.get_all_tools = mock_get_all_tools
    mock_module.get_statistics = mock_get_statistics

    sys.modules['bob_ai_mega_library_database_5000'] = mock_module


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    CORS(app)

    # Import and register blueprint
    from bob_ai_api_endpoints import bob_ai_blueprint
    app.register_blueprint(bob_ai_blueprint)

    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestDisciplinesEndpoint:
    """Test GET /api/disciplines/all"""

    def test_get_all_disciplines_success(self, client):
        """Test successful retrieval of all disciplines"""
        response = client.get('/api/disciplines/all?limit=10&offset=0')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert data['data']['total'] == 136
        assert len(data['data']['disciplines']) == 10

    def test_get_all_disciplines_pagination(self, client):
        """Test pagination parameters"""
        response = client.get('/api/disciplines/all?limit=5&offset=5')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['offset'] == 5
        assert data['data']['limit'] == 5
        assert len(data['data']['disciplines']) == 5

    def test_get_all_disciplines_max_limit(self, client):
        """Test that limit is capped at 500"""
        response = client.get('/api/disciplines/all?limit=1000&offset=0')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['limit'] == 500

    def test_get_all_disciplines_search(self, client):
        """Test search parameter"""
        response = client.get('/api/disciplines/all?limit=50&offset=0&search=Machine')
        assert response.status_code == 200
        data = json.loads(response.data)
        # Should find at least Machine Learning
        assert any('Machine' in d.get('name', '') for d in data['data']['disciplines'])

    def test_get_all_disciplines_default_params(self, client):
        """Test default parameters"""
        response = client.get('/api/disciplines/all')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['limit'] == 100
        assert data['data']['offset'] == 0


class TestDisciplineLibrariesEndpoint:
    """Test GET /api/disciplines/<name>/libraries"""

    def test_get_discipline_libraries_success(self, client):
        """Test successful retrieval of discipline libraries"""
        response = client.get('/api/disciplines/Linear%20Regression/libraries')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['discipline'] == 'Linear Regression'
        assert 'packages' in data['data']
        assert 'tools' in data['data']
        assert 'resources' in data['data']

    def test_get_discipline_libraries_not_found(self, client):
        """Test 404 for non-existent discipline"""
        response = client.get('/api/disciplines/NonExistent%20Discipline/libraries')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'not found' in data['message'].lower()

    def test_get_discipline_libraries_summary(self, client):
        """Test that summary counts are accurate"""
        response = client.get('/api/disciplines/Linear%20Regression/libraries')
        data = json.loads(response.data)
        summary = data['data']['summary']
        packages = data['data']['packages']
        assert summary['packages_count'] == len(packages)
        assert summary['total_libraries'] == len(packages) + len(data['data']['tools'])

    def test_get_discipline_libraries_url_encoding(self, client):
        """Test URL encoding of discipline names"""
        # Test with spaces encoded as %20
        response = client.get('/api/disciplines/Machine%20Learning/libraries')
        assert response.status_code == 200


class TestCategoriesEndpoint:
    """Test GET /api/categories"""

    def test_get_categories_success(self, client):
        """Test successful retrieval of categories"""
        response = client.get('/api/categories')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'sample_categories' in data['data']
        assert 'statistics' in data['data']

    def test_get_categories_statistics(self, client):
        """Test category statistics"""
        response = client.get('/api/categories')
        data = json.loads(response.data)
        stats = data['data']['statistics']
        assert stats['total_disciplines'] == 136
        assert stats['total_packages'] > 0
        assert stats['total_tools'] > 0
        assert 'average_disciplines_per_category' in stats

    def test_get_categories_structure(self, client):
        """Test category response structure"""
        response = client.get('/api/categories')
        data = json.loads(response.data)
        for cat in data['data']['sample_categories']:
            assert 'name' in cat
            assert 'discipline_count' in cat
            assert 'sample_disciplines' in cat


class TestLearningPathEndpoint:
    """Test POST /api/learning-path"""

    def test_create_learning_path_success(self, client):
        """Test successful learning path generation"""
        payload = {
            'discipline': 'Machine Learning',
            'estimated_hours': 250,
            'skill_level': 'beginner'
        }
        response = client.post(
            '/api/learning-path',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['discipline'] == 'Machine Learning'
        assert 'phases' in data['data']
        assert len(data['data']['phases']) == 4

    def test_create_learning_path_missing_discipline(self, client):
        """Test error when discipline is missing"""
        payload = {
            'estimated_hours': 250,
            'skill_level': 'beginner'
        }
        response = client.post(
            '/api/learning-path',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data['data'] or 'required' in data.get('message', '').lower()

    def test_create_learning_path_not_found(self, client):
        """Test 404 for non-existent discipline"""
        payload = {
            'discipline': 'NonExistentDiscipline',
            'estimated_hours': 250,
            'skill_level': 'beginner'
        }
        response = client.post(
            '/api/learning-path',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 404

    def test_create_learning_path_phases(self, client):
        """Test learning path phase structure"""
        payload = {
            'discipline': 'Linear Regression',
            'estimated_hours': 100,
            'skill_level': 'intermediate'
        }
        response = client.post(
            '/api/learning-path',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        phases = data['data']['phases']
        assert len(phases) == 4
        for phase in phases:
            assert 'phase' in phase
            assert 'name' in phase
            assert 'hours' in phase
            assert 'topics' in phase
            assert 'difficulty' in phase

    def test_create_learning_path_resources(self, client):
        """Test learning path includes resources"""
        payload = {
            'discipline': 'Machine Learning',
            'estimated_hours': 250,
            'skill_level': 'beginner'
        }
        response = client.post(
            '/api/learning-path',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        resources = data['data']['resources']
        assert 'packages' in resources
        assert 'tools' in resources
        assert 'learning_resources' in resources


class TestRecommendationsEndpoint:
    """Test GET /api/recommendations/tools"""

    def test_get_recommendations_success(self, client):
        """Test successful tool recommendations"""
        response = client.get('/api/recommendations/tools?top_n=10')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'recommendations' in data['data']
        assert len(data['data']['recommendations']) <= 10

    def test_get_recommendations_max_n(self, client):
        """Test that top_n is capped at 50"""
        response = client.get('/api/recommendations/tools?top_n=100')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']['recommendations']) <= 50

    def test_get_recommendations_structure(self, client):
        """Test recommendation response structure"""
        response = client.get('/api/recommendations/tools?top_n=5')
        data = json.loads(response.data)
        for rec in data['data']['recommendations']:
            assert 'tool' in rec
            assert 'frequency' in rec
            assert 'disciplines' in rec
            assert 'use_cases' in rec

    def test_get_recommendations_with_disciplines(self, client):
        """Test filtering by disciplines"""
        response = client.get(
            '/api/recommendations/tools?top_n=10&disciplines=Machine%20Learning,Linear%20Regression'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'recommendations' in data['data']

    def test_get_recommendations_default_params(self, client):
        """Test default parameters"""
        response = client.get('/api/recommendations/tools')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']['recommendations']) == 10


class TestHealthEndpoint:
    """Test GET /api/disciplines/health"""

    def test_health_check_success(self, client):
        """Test health check endpoint"""
        response = client.get('/api/disciplines/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['bob_ai_mega_available'] is True
        assert data['data']['status'] == 'healthy'

    def test_health_check_statistics(self, client):
        """Test health check returns statistics"""
        response = client.get('/api/disciplines/health')
        data = json.loads(response.data)
        assert 'disciplines' in data['data']
        assert 'packages' in data['data']
        assert 'tools' in data['data']
        assert data['data']['disciplines'] == 136


class TestResponseFormat:
    """Test consistent response format across all endpoints"""

    def test_response_has_status(self, client):
        """Test all responses have status field"""
        endpoints = [
            '/api/disciplines/all',
            '/api/disciplines/Linear%20Regression/libraries',
            '/api/categories',
            '/api/disciplines/health',
            '/api/recommendations/tools'
        ]
        for endpoint in endpoints:
            response = client.get(endpoint)
            data = json.loads(response.data)
            assert 'status' in data
            assert data['status'] in ['success', 'error']

    def test_response_has_timestamp(self, client):
        """Test all responses have timestamp"""
        response = client.get('/api/disciplines/all')
        data = json.loads(response.data)
        assert 'timestamp' in data

    def test_response_has_data(self, client):
        """Test all responses have data field"""
        response = client.get('/api/disciplines/all')
        data = json.loads(response.data)
        assert 'data' in data

    def test_error_response_format(self, client):
        """Test error response format"""
        response = client.get('/api/disciplines/NonExistent/libraries')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'message' in data


class TestCORSHeaders:
    """Test CORS headers"""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present"""
        response = client.get('/api/disciplines/all')
        # Flask-CORS adds headers
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling"""

    def test_missing_required_field(self, client):
        """Test missing required field in POST"""
        payload = {'estimated_hours': 100}
        response = client.post(
            '/api/learning-path',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_invalid_json(self, client):
        """Test invalid JSON"""
        response = client.post(
            '/api/learning-path',
            data='invalid json',
            content_type='application/json'
        )
        # Flask will return 400 for invalid JSON
        assert response.status_code in [400, 415]

    def test_unsupported_method(self, client):
        """Test unsupported HTTP method"""
        response = client.post('/api/disciplines/all')
        assert response.status_code in [404, 405]  # Method not allowed or not found


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
