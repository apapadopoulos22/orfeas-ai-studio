#!/usr/bin/env python3
"""
BOB AI v10.0 - PHASE 4 REST API ENDPOINTS
Production Deployment - API Layer

Implements all 8 REST API endpoints for Phase 3 knowledge system:
1. GET /api/disciplines - List all disciplines
2. GET /api/disciplines/{id} - Get discipline details
3. GET /api/disciplines/{id}/related - Get related disciplines
4. GET /api/knowledge-graph - Get knowledge graph
5. GET /api/disciplines/path/{from}/{to} - Find path between disciplines
6. GET /api/tier/{tier}/connections - Get tier connections
7. GET /api/statistics/phase3 - Get Phase 3 statistics
8. POST /api/query - Advanced query interface

Version: 1.0.0
Date: October 28, 2025
Status: PHASE 4 IMPLEMENTATION
"""

import sys
import os
# Get absolute path to backend directory
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

from flask import Blueprint, request, jsonify
from functools import wraps
from typing import Dict, Any, List, Optional
import logging
from bob_ai_discipline_mapper import get_discipline_mapper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint for Phase 4 API routes
phase4_api = Blueprint('phase4_api', __name__, url_prefix='/api')

# Initialize mapper (singleton)
mapper = get_discipline_mapper()


# ============================================================================
# MIDDLEWARE & UTILITIES
# ============================================================================

def handle_errors(f):
    """Decorator for consistent error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return jsonify({
                "error": "Validation error",
                "message": str(e),
                "status": 400
            }), 400
        except KeyError as e:
            logger.warning(f"Not found: {e}")
            return jsonify({
                "error": "Not found",
                "message": f"Discipline {str(e)} not found",
                "status": 404
            }), 404
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return jsonify({
                "error": "Internal server error",
                "message": str(e),
                "status": 500
            }), 500
    return decorated_function


def format_response(data: Any, meta: Optional[Dict] = None) -> Dict:
    """Format response with metadata"""
    response = {
        "success": True,
        "data": data,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }
    if meta:
        response["meta"] = meta
    return response


# ============================================================================
# ENDPOINT 1: GET /api/disciplines
# ============================================================================

@phase4_api.route('/disciplines', methods=['GET'])
@handle_errors
def get_disciplines():
    """
    Get list of all disciplines

    Query Parameters:
        - tier: Filter by tier (1-12)
        - category: Filter by category
        - limit: Max results (default: 100, max: 500)
        - offset: Pagination offset (default: 0)

    Returns:
        {
            "success": true,
            "data": {
                "disciplines": [...],
                "count": 403
            },
            "meta": {
                "tier": (optional),
                "category": (optional),
                "limit": int,
                "offset": int,
                "total": int
            }
        }
    """
    # Get filter parameters
    tier = request.args.get('tier', type=int)
    category = request.args.get('category', type=str)
    limit = min(int(request.args.get('limit', 100)), 500)
    offset = int(request.args.get('offset', 0))

    # Get all disciplines
    disciplines = mapper.get_all_disciplines()

    # Apply filters
    if tier:
        disciplines = mapper.get_disciplines_by_tier(tier)
    elif category:
        disciplines = mapper.get_disciplines_by_category(category)

    # Apply pagination
    total = len(disciplines)
    disciplines = disciplines[offset:offset+limit]

    return jsonify(format_response(
        data={
            "disciplines": disciplines,
            "count": len(disciplines)
        },
        meta={
            "limit": limit,
            "offset": offset,
            "total": total
        }
    ))


# ============================================================================
# ENDPOINT 2: GET /api/disciplines/{id}
# ============================================================================

@phase4_api.route('/disciplines/<discipline_id>', methods=['GET'])
@handle_errors
def get_discipline_detail(discipline_id: str):
    """
    Get detailed information about a discipline

    Path Parameters:
        - discipline_id: Name or ID of discipline

    Returns:
        {
            "success": true,
            "data": {
                "name": str,
                "category": str,
                "tier": int,
                "total_items": int,
                "keywords": [...],
                "system_prompt": str,
                "related_count": int
            }
        }
    """
    # Get discipline details
    details = mapper.get_discipline_details(discipline_id)

    if not details:
        raise KeyError(discipline_id)

    # Add related count
    related = mapper.get_related_disciplines(discipline_id)
    details['related_count'] = len(related) if related else 0

    return jsonify(format_response(data=details))


# ============================================================================
# ENDPOINT 3: GET /api/disciplines/{id}/related
# ============================================================================

@phase4_api.route('/disciplines/<discipline_id>/related', methods=['GET'])
@handle_errors
def get_related_disciplines_endpoint(discipline_id: str):
    """
    Get disciplines related to the specified discipline

    Path Parameters:
        - discipline_id: Name or ID of discipline

    Query Parameters:
        - max_results: Maximum results (default: 50)

    Returns:
        {
            "success": true,
            "data": {
                "discipline": str,
                "related": [...],
                "count": int
            }
        }
    """
    # Get related disciplines
    related = mapper.get_related_disciplines(discipline_id)

    if related is None:
        raise KeyError(discipline_id)

    max_results = int(request.args.get('max_results', 50))
    related = related[:max_results] if related else []

    return jsonify(format_response(data={
        "discipline": discipline_id,
        "related": related,
        "count": len(related)
    }))


# ============================================================================
# ENDPOINT 4: GET /api/knowledge-graph
# ============================================================================

@phase4_api.route('/knowledge-graph', methods=['GET'])
@handle_errors
def get_knowledge_graph_endpoint():
    """
    Get complete knowledge graph (nodes and edges)

    Query Parameters:
        - include_stats: Include statistics (default: true)

    Returns:
        {
            "success": true,
            "data": {
                "nodes": [...403 nodes...],
                "edges": [...64 edges...],
                "statistics": {...},
                "graph_metrics": {
                    "avg_degree": float,
                    "diameter": int,
                    "density": float
                }
            }
        }
    """
    # Get knowledge graph
    graph = mapper.get_knowledge_graph()

    include_stats = request.args.get('include_stats', 'true').lower() == 'true'

    data = {
        "nodes": graph['nodes'],
        "edges": graph['edges'],
    }

    if include_stats:
        data['statistics'] = graph['statistics']
        # Calculate additional graph metrics
        num_nodes = len(graph['nodes'])
        num_edges = len(graph['edges'])
        avg_degree = (2 * num_edges) / num_nodes if num_nodes > 0 else 0

        data['graph_metrics'] = {
            "avg_degree": round(avg_degree, 2),
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "edge_density": round(num_edges / (num_nodes * (num_nodes - 1) / 2), 4) if num_nodes > 1 else 0
        }

    return jsonify(format_response(data=data))


# ============================================================================
# ENDPOINT 5: GET /api/disciplines/path/{from_disc}/{to_disc}
# ============================================================================

@phase4_api.route('/disciplines/path/<from_disc>/<to_disc>', methods=['GET'])
@handle_errors
def find_path_endpoint(from_disc: str, to_disc: str):
    """
    Find shortest path between two disciplines

    Path Parameters:
        - from_disc: Starting discipline
        - to_disc: Ending discipline

    Query Parameters:
        - max_depth: Maximum path depth (default: 5)

    Returns:
        {
            "success": true,
            "data": {
                "from": str,
                "to": str,
                "path": [...],
                "path_length": int,
                "found": boolean
            }
        }
    """
    # Get max depth parameter
    max_depth = int(request.args.get('max_depth', 5))

    # Find path using BFS
    path = mapper.find_discipline_path(from_disc, to_disc, max_depth=max_depth)

    return jsonify(format_response(data={
        "from": from_disc,
        "to": to_disc,
        "path": path if path else [],
        "path_length": len(path) - 1 if path else -1,
        "found": path is not None
    }))


# ============================================================================
# ENDPOINT 6: GET /api/tier/{tier}/connections
# ============================================================================

@phase4_api.route('/tier/<int:tier>/connections', methods=['GET'])
@handle_errors
def get_tier_connections_endpoint(tier: int):
    """
    Get cross-tier connections for a specific tier

    Path Parameters:
        - tier: Tier number (1-12)

    Returns:
        {
            "success": true,
            "data": {
                "tier": int,
                "disciplines": int,
                "connections": {...},
                "cross_tier_links": int
            }
        }
    """
    # Validate tier
    if tier < 1 or tier > 12:
        raise ValueError(f"Tier must be between 1 and 12, got {tier}")

    # Get tier connections
    connections = mapper.get_tier_connections(tier)

    return jsonify(format_response(data=connections))


# ============================================================================
# ENDPOINT 7: GET /api/statistics/phase3
# ============================================================================

@phase4_api.route('/statistics/phase3', methods=['GET'])
@handle_errors
def get_phase3_statistics_endpoint():
    """
    Get comprehensive Phase 3 statistics

    Returns:
        {
            "success": true,
            "data": {
                "phase": str,
                "total_disciplines": int,
                "total_knowledge_items": int,
                "semantic_relationships": int,
                "average_relationships_per_discipline": float,
                "knowledge_graph_edges": int,
                "cross_tier_links": int,
                "tier_breakdown": {...}
            }
        }
    """
    # Get statistics
    stats = mapper.get_phase3_statistics()

    return jsonify(format_response(data=stats))


# ============================================================================
# ENDPOINT 8: POST /api/query
# ============================================================================

@phase4_api.route('/query', methods=['POST'])
@handle_errors
def advanced_query():
    """
    Advanced query interface

    Request Body:
        {
            "query_type": "semantic_search|related|pathfinding|tier_analysis",
            "params": {...}
        }

    Query Types:
        1. semantic_search
           params: {query: str, limit: int}

        2. related
           params: {discipline: str, max_results: int}

        3. pathfinding
           params: {from: str, to: str, max_depth: int}

        4. tier_analysis
           params: {tier: int}

    Returns:
        {
            "success": true,
            "data": {...results...}
        }
    """
    # Get request data
    data = request.get_json()

    if not data:
        raise ValueError("Request body must be JSON")

    query_type = data.get('query_type')
    params = data.get('params', {})

    if not query_type:
        raise ValueError("query_type is required")

    # Handle different query types
    if query_type == 'semantic_search':
        # Search for semantically related items
        query = params.get('query')
        limit = params.get('limit', 50)

        if not query:
            raise ValueError("query parameter required")

        results = mapper.search_knowledge(query)[:limit]

        return jsonify(format_response(data={
            "query_type": query_type,
            "query": query,
            "results": results,
            "count": len(results)
        }))

    elif query_type == 'related':
        # Get related disciplines
        discipline = params.get('discipline')
        max_results = params.get('max_results', 50)

        if not discipline:
            raise ValueError("discipline parameter required")

        related = mapper.get_related_disciplines(discipline)
        related = related[:max_results] if related else []

        return jsonify(format_response(data={
            "query_type": query_type,
            "discipline": discipline,
            "related": related,
            "count": len(related)
        }))

    elif query_type == 'pathfinding':
        # Find path between disciplines
        from_disc = params.get('from')
        to_disc = params.get('to')
        max_depth = params.get('max_depth', 5)

        if not from_disc or not to_disc:
            raise ValueError("from and to parameters required")

        path = mapper.find_discipline_path(from_disc, to_disc, max_depth=max_depth)

        return jsonify(format_response(data={
            "query_type": query_type,
            "from": from_disc,
            "to": to_disc,
            "path": path if path else [],
            "path_length": len(path) - 1 if path else -1,
            "found": path is not None
        }))

    elif query_type == 'tier_analysis':
        # Analyze tier connections
        tier = params.get('tier')

        if not tier:
            raise ValueError("tier parameter required")

        connections = mapper.get_tier_connections(tier)

        return jsonify(format_response(data={
            "query_type": query_type,
            "tier_analysis": connections
        }))

    else:
        raise ValueError(f"Unknown query_type: {query_type}")


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@phase4_api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "phase": "4",
        "version": "1.0.0",
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    })


@phase4_api.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check - verifies all systems operational"""
    try:
        # Check if mapper is initialized
        disciplines = mapper.get_all_disciplines()

        if len(disciplines) >= 391:
            return jsonify({
                "ready": True,
                "disciplines_loaded": len(disciplines),
                "version": "1.0.0"
            })
        else:
            return jsonify({
                "ready": False,
                "error": f"Only {len(disciplines)} disciplines loaded, expected >=391"
            }), 503

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            "ready": False,
            "error": str(e)
        }), 503


# ============================================================================
# EXPORT
# ============================================================================

def register_phase4_routes(app):
    """Register Phase 4 API routes with Flask app"""
    app.register_blueprint(phase4_api)
    logger.info("Phase 4 API routes registered successfully")


if __name__ == "__main__":
    print("BOB AI v10.0 - Phase 4 REST API Endpoints")
    print("This module should be imported into main Flask app")
    print(f"Total endpoints: 8 + 2 health checks = 10")
