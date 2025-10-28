#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOB AI Mega Expansion - REST API Endpoints
===========================================

This module provides 5 new REST API endpoints for the BOB AI mega expansion:
- GET /api/disciplines/all - Get all available disciplines
- GET /api/disciplines/<name>/libraries - Get libraries for a specific discipline
- GET /api/categories - Get all categories (structure)
- POST /api/learning-path - Generate learning path for a discipline
- GET /api/recommendations/tools - Get tool recommendations

Integration: Add these blueprints to main.py
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from functools import wraps

from flask import Blueprint, request, jsonify, Response
from flask_cors import cross_origin

# Import BOB AI mega library
try:
    from bob_ai_mega_library_database_5000 import (
        DISCIPLINE_LIBRARY_MAP,
        get_discipline_libraries,
        get_all_python_packages,
        get_all_tools,
        get_all_resources,
        get_statistics,
    )
    BOB_AI_MEGA_AVAILABLE = True
except ImportError as e:
    BOB_AI_MEGA_AVAILABLE = False
    import sys
    print(f"Warning: BOB AI Mega Library import failed: {e}", file=sys.stderr)

# Setup logging
logger = logging.getLogger(__name__)

# Create Blueprint
bob_ai_blueprint = Blueprint(
    'bob_ai_disciplines',
    __name__,
    url_prefix='/api'
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def bob_ai_enabled(f):
    """Decorator to check if BOB AI mega library is available"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not BOB_AI_MEGA_AVAILABLE:
            return jsonify({
                'error': 'BOB AI Mega Library not available',
                'status': 503
            }), 503
        return f(*args, **kwargs)
    return decorated_function


def create_response(data: Any, status: int = 200, message: str = None) -> Tuple[Dict, int]:
    """Create standardized API response"""
    response = {
        'status': 'success' if status == 200 else 'error',
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    }
    if message:
        response['message'] = message
    return jsonify(response), status


# ============================================================================
# API ENDPOINTS
# ============================================================================

@bob_ai_blueprint.route('/disciplines/all', methods=['GET'])
@cross_origin()
@bob_ai_enabled
def get_all_disciplines():
    """
    GET /api/disciplines/all

    Returns all available disciplines with their metadata.

    Query Parameters:
        - limit: Max number of disciplines (default: 100, max: 500)
        - offset: Pagination offset (default: 0)
        - search: Search term to filter disciplines

    Response:
        {
            "status": "success",
            "timestamp": "2025-10-28T09:15:00",
            "data": {
                "total": 136,
                "returned": 10,
                "offset": 0,
                "disciplines": [
                    {
                        "name": "Linear Regression",
                        "packages_count": 3,
                        "tools_count": 3,
                        "resources_count": 3
                    },
                    ...
                ]
            }
        }
    """
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 100)), 500)
        offset = int(request.args.get('offset', 0))
        search_term = request.args.get('search', '').lower()

        # Get all disciplines
        all_disciplines = list(DISCIPLINE_LIBRARY_MAP.keys())

        # Filter if search term provided
        if search_term:
            all_disciplines = [d for d in all_disciplines if search_term in d.lower()]

        # Get total count before pagination
        total_count = len(all_disciplines)

        # Apply pagination
        paginated = all_disciplines[offset:offset + limit]

        # Build response data
        disciplines_data = []
        for discipline_name in paginated:
            libs = get_discipline_libraries(discipline_name)
            if libs:
                disciplines_data.append({
                    'name': discipline_name,
                    'packages_count': len(libs.get('packages', [])),
                    'tools_count': len(libs.get('tools', [])),
                    'resources_count': len(libs.get('resources', [])),
                })

        response_data = {
            'total': total_count,
            'returned': len(disciplines_data),
            'offset': offset,
            'limit': limit,
            'disciplines': disciplines_data
        }

        logger.info(f"[API] GET /api/disciplines/all - Returned {len(disciplines_data)} disciplines")
        return create_response(response_data)

    except Exception as e:
        logger.error(f"[ERROR] GET /api/disciplines/all: {e}")
        return create_response({'error': str(e)}, 500, f"Error: {e}")


@bob_ai_blueprint.route('/disciplines/<name>/libraries', methods=['GET'])
@cross_origin()
@bob_ai_enabled
def get_discipline_libraries_endpoint(name: str):
    """
    GET /api/disciplines/<name>/libraries

    Returns all libraries, tools, and resources for a specific discipline.

    Path Parameters:
        - name: Discipline name (URL-encoded)

    Response:
        {
            "status": "success",
            "timestamp": "2025-10-28T09:15:00",
            "data": {
                "discipline": "Linear Regression",
                "packages": ["scikit-learn", "statsmodels", "scipy"],
                "tools": ["jupyter", "numpy", "pandas"],
                "resources": ["scikit-learn docs", "Statistics tutorial"],
                "summary": {
                    "packages_count": 3,
                    "tools_count": 3,
                    "resources_count": 2,
                    "total_libraries": 8
                }
            }
        }
    """
    try:
        # Get libraries for discipline
        libs = get_discipline_libraries(name)

        if not libs:
            logger.warning(f"[API] GET /api/disciplines/{name}/libraries - Not found")
            return create_response(
                {'error': f'Discipline "{name}" not found'},
                404,
                f'Discipline "{name}" not found'
            )

        response_data = {
            'discipline': name,
            'packages': libs.get('packages', []),
            'tools': libs.get('tools', []),
            'resources': libs.get('resources', []),
            'summary': {
                'packages_count': len(libs.get('packages', [])),
                'tools_count': len(libs.get('tools', [])),
                'resources_count': len(libs.get('resources', [])),
                'total_libraries': len(libs.get('packages', [])) + len(libs.get('tools', []))
            }
        }

        logger.info(f"[API] GET /api/disciplines/{name}/libraries - Success")
        return create_response(response_data)

    except Exception as e:
        logger.error(f"[ERROR] GET /api/disciplines/{name}/libraries: {e}")
        return create_response({'error': str(e)}, 500, f"Error: {e}")


@bob_ai_blueprint.route('/categories', methods=['GET'])
@cross_origin()
@bob_ai_enabled
def get_categories():
    """
    GET /api/categories

    Returns the category structure with discipline groupings.

    Response:
        {
            "status": "success",
            "timestamp": "2025-10-28T09:15:00",
            "data": {
                "total_categories": 1000,
                "sample_categories": [
                    {
                        "name": "AI & Machine Learning",
                        "discipline_count": 136,
                        "sample_disciplines": ["Linear Regression", "Decision Trees", ...]
                    },
                    ...
                ],
                "statistics": {
                    "total_disciplines": 136,
                    "average_disciplines_per_category": 0.136
                }
            }
        }
    """
    try:
        # Get statistics
        stats = get_statistics()

        # Build category structure (simplified - based on available disciplines)
        categories = {
            'AI & Machine Learning': [],
            'Data Science & Analytics': [],
            'Software Engineering': [],
            'DevOps & Cloud': [],
            'Emerging Technologies': []
        }

        # Categorize disciplines (simple keyword-based categorization)
        ai_keywords = ['regression', 'tree', 'forest', 'neural', 'cnn', 'rnn', 'lstm', 'transformer', 'learning', 'clustering']
        data_keywords = ['pandas', 'numpy', 'data', 'statistics', 'visualization', 'time series', 'database', 'sql']
        sw_keywords = ['python', 'javascript', 'java', 'c++', 'react', 'django', 'flask', 'api', 'testing']
        devops_keywords = ['docker', 'kubernetes', 'aws', 'terraform', 'ansible', 'ci/cd', 'monitoring']

        for discipline in DISCIPLINE_LIBRARY_MAP.keys():
            disc_lower = discipline.lower()
            if any(kw in disc_lower for kw in ai_keywords):
                categories['AI & Machine Learning'].append(discipline)
            elif any(kw in disc_lower for kw in data_keywords):
                categories['Data Science & Analytics'].append(discipline)
            elif any(kw in disc_lower for kw in sw_keywords):
                categories['Software Engineering'].append(discipline)
            elif any(kw in disc_lower for kw in devops_keywords):
                categories['DevOps & Cloud'].append(discipline)
            else:
                categories['Emerging Technologies'].append(discipline)

        # Build response
        response_data = {
            'total_categories': 1000,  # Planned
            'categories_defined': len(categories),
            'sample_categories': [
                {
                    'name': cat_name,
                    'discipline_count': len(disciplines),
                    'sample_disciplines': disciplines[:5]
                }
                for cat_name, disciplines in categories.items()
            ],
            'statistics': {
                'total_disciplines': stats['total_disciplines'],
                'total_packages': stats['unique_python_packages'],
                'total_tools': stats['unique_cli_tools'],
                'average_disciplines_per_category': round(stats['total_disciplines'] / len(categories), 2)
            }
        }

        logger.info("[API] GET /api/categories - Success")
        return create_response(response_data)

    except Exception as e:
        logger.error(f"[ERROR] GET /api/categories: {e}")
        return create_response({'error': str(e)}, 500, f"Error: {e}")


@bob_ai_blueprint.route('/learning-path', methods=['POST'])
@cross_origin()
@bob_ai_enabled
def create_learning_path():
    """
    POST /api/learning-path

    Generates a learning path for mastering a discipline.

    Request Body:
        {
            "discipline": "Machine Learning",  # Required
            "estimated_hours": 250,            # Optional (default: 250)
            "skill_level": "beginner"          # Optional: beginner|intermediate|advanced
        }

    Response:
        {
            "status": "success",
            "timestamp": "2025-10-28T09:15:00",
            "data": {
                "discipline": "Machine Learning",
                "estimated_hours": 250,
                "phases": [
                    {
                        "phase": 1,
                        "name": "Fundamentals",
                        "hours": 30,
                        "topics": ["Python Basics", "Math Fundamentals"]
                    },
                    ...
                ],
                "resources": {
                    "packages": [...],
                    "tools": [...],
                    "learning_resources": [...]
                }
            }
        }
    """
    try:
        # Get request data
        data = request.get_json()
        discipline = data.get('discipline', '').strip()
        estimated_hours = data.get('estimated_hours', 250)
        skill_level = data.get('skill_level', 'beginner').lower()

        if not discipline:
            return create_response(
                {'error': 'discipline parameter is required'},
                400,
                'Missing required parameter: discipline'
            )

        # Verify discipline exists
        libs = get_discipline_libraries(discipline)
        if not libs:
            return create_response(
                {'error': f'Discipline "{discipline}" not found'},
                404,
                f'Discipline "{discipline}" not found'
            )

        # Create learning path phases
        phases = [
            {
                'phase': 1,
                'name': 'Fundamentals',
                'hours': int(estimated_hours * 0.15),
                'topics': ['Basic Concepts', 'Theory Introduction'],
                'difficulty': 'beginner'
            },
            {
                'phase': 2,
                'name': 'Core Concepts',
                'hours': int(estimated_hours * 0.30),
                'topics': ['Deep Dive', 'Hands-on Practice'],
                'difficulty': 'intermediate'
            },
            {
                'phase': 3,
                'name': 'Advanced Topics',
                'hours': int(estimated_hours * 0.30),
                'topics': ['Complex Scenarios', 'Optimization'],
                'difficulty': 'advanced'
            },
            {
                'phase': 4,
                'name': 'Capstone Project',
                'hours': int(estimated_hours * 0.25),
                'topics': ['Real-world Application', 'Portfolio Building'],
                'difficulty': 'advanced'
            }
        ]

        response_data = {
            'discipline': discipline,
            'estimated_hours': estimated_hours,
            'skill_level': skill_level,
            'phases': phases,
            'resources': {
                'packages': libs.get('packages', []),
                'tools': libs.get('tools', []),
                'learning_resources': libs.get('resources', [])
            },
            'total_phases': len(phases),
            'completion_weeks': round(estimated_hours / (10 * 7), 1)  # Assuming 10h/week
        }

        logger.info(f"[API] POST /api/learning-path - Created path for {discipline}")
        return create_response(response_data, 200, f"Learning path created for {discipline}")

    except Exception as e:
        logger.error(f"[ERROR] POST /api/learning-path: {e}")
        return create_response({'error': str(e)}, 500, f"Error: {e}")


@bob_ai_blueprint.route('/recommendations/tools', methods=['GET'])
@cross_origin()
@bob_ai_enabled
def get_tool_recommendations():
    """
    GET /api/recommendations/tools

    Returns tool recommendations based on disciplines or use cases.

    Query Parameters:
        - disciplines: Comma-separated discipline names (optional)
        - use_case: Specific use case (optional)
        - top_n: Number of recommendations (default: 10, max: 50)

    Response:
        {
            "status": "success",
            "timestamp": "2025-10-28T09:15:00",
            "data": {
                "recommendations": [
                    {
                        "tool": "jupyter",
                        "frequency": 45,
                        "disciplines": ["Linear Regression", "Decision Trees", ...],
                        "use_cases": ["Development", "Research", "Education"]
                    },
                    ...
                ],
                "total_recommendations": 10
            }
        }
    """
    try:
        # Get query parameters
        disciplines_param = request.args.get('disciplines', '').split(',')
        disciplines_param = [d.strip() for d in disciplines_param if d.strip()]
        top_n = min(int(request.args.get('top_n', 10)), 50)

        # Get all tools with frequency
        tool_frequency = {}
        tool_disciplines = {}

        if disciplines_param:
            # Count tools from specified disciplines
            for disc in disciplines_param:
                libs = get_discipline_libraries(disc)
                if libs:
                    for tool in libs.get('tools', []):
                        tool_frequency[tool] = tool_frequency.get(tool, 0) + 1
                        if tool not in tool_disciplines:
                            tool_disciplines[tool] = []
                        tool_disciplines[tool].append(disc)
        else:
            # Count tools from all disciplines
            for discipline_libs in DISCIPLINE_LIBRARY_MAP.values():
                for tool in discipline_libs.get('tools', []):
                    tool_frequency[tool] = tool_frequency.get(tool, 0) + 1

        # Sort by frequency and get top N
        sorted_tools = sorted(tool_frequency.items(), key=lambda x: x[1], reverse=True)
        top_tools = sorted_tools[:top_n]

        # Build recommendations
        recommendations = [
            {
                'tool': tool,
                'frequency': count,
                'disciplines': tool_disciplines.get(tool, [])[:5],
                'use_cases': ['Development', 'Research', 'Production']
            }
            for tool, count in top_tools
        ]

        response_data = {
            'recommendations': recommendations,
            'total_recommendations': len(recommendations),
            'based_on': 'all' if not disciplines_param else f"{len(disciplines_param)} disciplines"
        }

        logger.info(f"[API] GET /api/recommendations/tools - Returned {len(recommendations)} tools")
        return create_response(response_data)

    except Exception as e:
        logger.error(f"[ERROR] GET /api/recommendations/tools: {e}")
        return create_response({'error': str(e)}, 500, f"Error: {e}")


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@bob_ai_blueprint.route('/disciplines/health', methods=['GET'])
@cross_origin()
def health_check():
    """Simple health check for BOB AI endpoints"""
    if BOB_AI_MEGA_AVAILABLE:
        stats = get_statistics()
        return create_response({
            'status': 'healthy',
            'bob_ai_mega_available': True,
            'disciplines': stats['total_disciplines'],
            'packages': stats['unique_python_packages'],
            'tools': stats['unique_cli_tools']
        }, 200, "BOB AI Mega Expansion endpoints are operational")
    else:
        return create_response(
            {'status': 'unavailable', 'bob_ai_mega_available': False},
            503,
            "BOB AI Mega Expansion not available"
        )


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@bob_ai_blueprint.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return create_response({'error': 'Endpoint not found'}, 404, 'Resource not found')


@bob_ai_blueprint.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"[ERROR] Internal server error: {error}")
    return create_response({'error': 'Internal server error'}, 500, 'An error occurred')
