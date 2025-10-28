"""
BOB AI Expansion - Phase 2: Enhanced API Endpoints
=================================================

Extends Phase 1 API with knowledge graph, recommendations, and advanced search.

New Endpoints (Phase 2):
  - GET /api/v2/graph/analyze/{discipline_id}
  - GET /api/v2/graph/prerequisites/{discipline_id}
  - GET /api/v2/recommendations (based on completed disciplines)
  - POST /api/v2/search/advanced (semantic search)
  - GET /api/v2/learning-paths/optimized/{target_id}
  - GET /api/v2/skill-gaps/analyze/{target_id}

Author: ORFEAS AI - BOB AI Expansion v10.0
Date: October 28, 2025
"""

import logging
import time
from functools import wraps
from typing import Optional, List, Set

from flask import Blueprint, request, jsonify, current_app

logger = logging.getLogger(__name__)

# Create blueprint
bob_ai_phase2_bp = Blueprint(
    'bob_ai_phase2',
    __name__,
    url_prefix='/api/v2'
)


def require_session(f):
    """Decorator to inject database session"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        Session = current_app.config.get('BOB_AI_SESSION')
        if not Session:
            return jsonify({'error': 'Database not configured'}), 503

        session = Session()
        try:
            return f(*args, session=session, **kwargs)
        except Exception as e:
            logger.error(f"Endpoint error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()

    return decorated_function


def require_graph(f):
    """Decorator to ensure knowledge graph is available"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        graph_analyzer = current_app.config.get('BOB_AI_GRAPH_ANALYZER')
        recommendation_engine = current_app.config.get('BOB_AI_RECOMMENDATION_ENGINE')

        if not graph_analyzer or not recommendation_engine:
            return jsonify({
                'error': 'Knowledge graph not initialized',
                'message': 'Run: python -m bob_ai_expansion_data_loader --initialize-graph'
            }), 503

        return f(*args,
                 graph_analyzer=graph_analyzer,
                 recommendation_engine=recommendation_engine,
                 **kwargs)

    return decorated_function


def require_search(f):
    """Decorator to ensure search engine is available"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        search_engine = current_app.config.get('BOB_AI_SEARCH_ENGINE')

        if not search_engine:
            return jsonify({
                'error': 'Search engine not initialized',
                'message': 'Install SearchEngine dependency'
            }), 503

        return f(*args, search_engine=search_engine, **kwargs)

    return decorated_function


# ============================================================================
# KNOWLEDGE GRAPH ENDPOINTS
# ============================================================================

@bob_ai_phase2_bp.route('/graph/analyze/<int:discipline_id>', methods=['GET'])
@require_session
@require_graph
def analyze_discipline_graph(discipline_id, session=None, graph_analyzer=None, recommendation_engine=None):
    """
    Analyze discipline relationships in knowledge graph

    Returns:
      - Prerequisites (ordered learning path)
      - Related disciplines
      - Community clustering
      - Centrality metrics
    """
    try:
        # Get prerequisites
        prerequisites = graph_analyzer.get_prerequisites_ordered(discipline_id)

        # Get related disciplines
        related = graph_analyzer.get_related_disciplines(discipline_id, depth=2)

        # Get centrality (importance in network)
        centrality = graph_analyzer.compute_centrality()
        node_centrality = centrality.get(discipline_id, 0.0)

        # Get PageRank (overall importance)
        pagerank = graph_analyzer.compute_pagerank()
        node_pagerank = pagerank.get(discipline_id, 0.0)

        return jsonify({
            'discipline_id': discipline_id,
            'prerequisites': prerequisites,
            'prerequisites_count': len(prerequisites),
            'related_disciplines': [
                {
                    'discipline_id': disc_id,
                    'relationship_strength': round(strength, 2)
                }
                for disc_id, strength in related
            ],
            'network_metrics': {
                'centrality': round(node_centrality, 3),
                'pagerank': round(node_pagerank * 100, 2),
                'importance_rank': 'High' if node_pagerank > 0.01 else 'Medium' if node_pagerank > 0.005 else 'Low'
            },
            'clusters': graph_analyzer.find_learning_clusters(),
        }), 200

    except ValueError:
        return jsonify({'error': f'Discipline {discipline_id} not found'}), 404
    except Exception as e:
        logger.error(f"Graph analysis error: {e}")
        return jsonify({'error': str(e)}), 500


@bob_ai_phase2_bp.route('/graph/prerequisites/<int:discipline_id>', methods=['GET'])
@require_session
@require_graph
def get_prerequisites(discipline_id, session=None, graph_analyzer=None, recommendation_engine=None):
    """Get prerequisite chain for a discipline (learning path)"""
    try:
        prerequisites = graph_analyzer.get_prerequisites_ordered(discipline_id)

        # Fetch full details for each prerequisite
        from bob_ai_expansion_phase1_database import ExpandedDiscipline

        prerequisites_details = []
        for prereq_id in prerequisites:
            prereq = session.query(ExpandedDiscipline).filter_by(id=prereq_id).first()
            if prereq:
                prerequisites_details.append({
                    'id': prereq.id,
                    'name': prereq.name,
                    'difficulty': prereq.difficulty_level,
                    'hours': prereq.estimated_hours,
                    'position_in_chain': len(prerequisites_details) + 1
                })

        total_hours = sum(p['hours'] for p in prerequisites_details)

        return jsonify({
            'target_discipline_id': discipline_id,
            'prerequisites': prerequisites_details,
            'prerequisite_count': len(prerequisites_details),
            'total_prerequisite_hours': total_hours,
            'recommended_sequence': 'Top-to-bottom',
        }), 200

    except Exception as e:
        logger.error(f"Prerequisites error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# RECOMMENDATION ENDPOINTS
# ============================================================================

@bob_ai_phase2_bp.route('/recommendations', methods=['GET'])
@require_session
@require_graph
def get_recommendations(session=None, graph_analyzer=None, recommendation_engine=None):
    """
    Get personalized recommendations based on completed disciplines

    Query Parameters:
      - completed: comma-separated discipline IDs already completed
      - difficulty: "progressive" (increase difficulty) or "lateral" (same level)
      - skill: optional target skill to work towards
      - limit: number of recommendations (default 5)
    """
    try:
        # Parse query parameters
        completed_str = request.args.get('completed', '')
        difficulty_pref = request.args.get('difficulty', 'progressive')
        target_skill = request.args.get('skill')
        limit = int(request.args.get('limit', 5))

        # Parse completed discipline IDs
        completed_disciplines = []
        if completed_str:
            try:
                completed_disciplines = [int(x.strip()) for x in completed_str.split(',')]
            except ValueError:
                return jsonify({'error': 'Invalid completed discipline IDs'}), 400

        if not completed_disciplines:
            return jsonify({
                'error': 'At least one completed discipline required',
                'message': 'Pass completed discipline IDs as query parameter: ?completed=1,2,3'
            }), 400

        # Get recommendations
        recommendations = recommendation_engine.recommend_next_disciplines(
            completed_disciplines=completed_disciplines,
            target_skill=target_skill,
            difficulty_preference=difficulty_pref,
            limit=limit
        )

        return jsonify({
            'recommendations': [r.to_dict() for r in recommendations],
            'recommendation_count': len(recommendations),
            'completed_disciplines': completed_disciplines,
            'difficulty_preference': difficulty_pref,
        }), 200

    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# LEARNING PATH ENDPOINTS
# ============================================================================

@bob_ai_phase2_bp.route('/learning-paths/optimized/<int:target_id>', methods=['GET'])
@require_session
@require_graph
def get_optimized_learning_path(target_id, session=None, graph_analyzer=None, recommendation_engine=None):
    """
    Generate optimized learning path to reach target discipline

    Query Parameters:
      - current_level: beginner/intermediate/advanced/expert (default: beginner)
    """
    try:
        current_level = request.args.get('current_level', 'beginner')

        # Generate optimized path
        path = recommendation_engine.recommend_learning_path(
            target_discipline_id=target_id,
            current_level=current_level
        )

        return jsonify(path.to_dict()), 200

    except Exception as e:
        logger.error(f"Learning path error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SKILL GAP ANALYSIS ENDPOINTS
# ============================================================================

@bob_ai_phase2_bp.route('/skill-gaps/analyze/<int:target_id>', methods=['GET', 'POST'])
@require_session
@require_graph
def analyze_skill_gaps(target_id, session=None, graph_analyzer=None, recommendation_engine=None):
    """
    Analyze skill gaps to reach target discipline

    GET: Returns gap analysis with empty user skills
    POST: Body: {skills: ['Python', 'Data Science', ...]}
          Returns gap analysis with analysis
    """
    try:
        # Get user skills
        user_skills = set()
        if request.method == 'POST':
            data = request.get_json() or {}
            user_skills = set(data.get('skills', []))

        # Analyze gaps
        gap_analysis = recommendation_engine.analyze_skill_gaps(
            user_skills=user_skills,
            target_discipline_id=target_id
        )

        return jsonify(gap_analysis), 200

    except Exception as e:
        logger.error(f"Skill gap analysis error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ADVANCED SEARCH ENDPOINTS
# ============================================================================

@bob_ai_phase2_bp.route('/search/advanced', methods=['POST'])
@require_session
@require_search
def advanced_search(session=None, search_engine=None):
    """
    Execute advanced search with filters

    Body:
    {
        "query": "machine learning",
        "filters": {
            "categories": ["AI/ML", "Data Science"],
            "difficulty": ["intermediate", "advanced"],
            "languages": ["python"],
            "estimated_hours_min": 5,
            "estimated_hours_max": 40
        },
        "limit": 20
    }
    """
    try:
        from bob_ai_expansion_phase2_search import FacetFilters

        data = request.get_json() or {}
        query = data.get('query', '')

        if not query:
            return jsonify({'error': 'Query parameter required'}), 400

        # Parse filters
        filters_data = data.get('filters', {})
        filters = FacetFilters(
            categories=filters_data.get('categories'),
            difficulty=filters_data.get('difficulty'),
            languages=filters_data.get('languages'),
            technology_stack=filters_data.get('technology_stack'),
            estimated_hours_min=filters_data.get('estimated_hours_min'),
            estimated_hours_max=filters_data.get('estimated_hours_max'),
            industry_focus=filters_data.get('industry_focus'),
        )

        limit = data.get('limit', 20)

        # Execute search
        search_response = search_engine.search(query, filters, limit)

        return jsonify(search_response.to_dict()), 200

    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        return jsonify({'error': str(e)}), 500


@bob_ai_phase2_bp.route('/search/by-skill', methods=['GET', 'POST'])
@require_session
@require_search
def search_by_skill(session=None, search_engine=None):
    """Search for disciplines teaching specific skills"""
    try:
        skills = set()

        if request.method == 'GET':
            skills_str = request.args.get('skills', '')
            if skills_str:
                skills = set(s.strip() for s in skills_str.split(','))
        else:
            data = request.get_json() or {}
            skills = set(data.get('skills', []))

        if not skills:
            return jsonify({'error': 'At least one skill required'}), 400

        results = search_engine.search_by_skill(skills)

        return jsonify({
            'skills': list(skills),
            'results': [r.to_dict() for r in results],
            'result_count': len(results),
        }), 200

    except Exception as e:
        logger.error(f"Skill search error: {e}")
        return jsonify({'error': str(e)}), 500


@bob_ai_phase2_bp.route('/search/by-industry', methods=['GET'])
@require_session
@require_search
def search_by_industry(session=None, search_engine=None):
    """Search for disciplines relevant to specific industry"""
    try:
        industry = request.args.get('industry')

        if not industry:
            return jsonify({'error': 'Industry parameter required'}), 400

        results = search_engine.search_by_industry(industry)

        return jsonify({
            'industry': industry,
            'results': [r.to_dict() for r in results],
            'result_count': len(results),
        }), 200

    except Exception as e:
        logger.error(f"Industry search error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@bob_ai_phase2_bp.route('/health', methods=['GET'])
@require_session
def phase2_health_check(session=None):
    """Check Phase 2 health (graph, search, recommendations)"""
    try:
        graph_analyzer = current_app.config.get('BOB_AI_GRAPH_ANALYZER')
        search_engine = current_app.config.get('BOB_AI_SEARCH_ENGINE')
        recommendation_engine = current_app.config.get('BOB_AI_RECOMMENDATION_ENGINE')

        health_status = {
            'service': 'BOB AI Expansion Phase 2',
            'status': 'healthy',
            'components': {
                'knowledge_graph': 'initialized' if graph_analyzer else 'not_initialized',
                'search_engine': 'initialized' if search_engine else 'not_initialized',
                'recommendations': 'initialized' if recommendation_engine else 'not_initialized',
            }
        }

        if search_engine:
            search_health = search_engine.health_check()
            health_status['components']['search_backend'] = search_health

        return jsonify(health_status), 200

    except Exception as e:
        return jsonify({'status': 'degraded', 'error': str(e)}), 503


# ============================================================================
# BLUEPRINT REGISTRATION
# ============================================================================

def init_bob_ai_phase2_api(app, Session, graph_analyzer, recommendation_engine, search_engine):
    """
    Register Phase 2 API with Flask app

    Args:
        app: Flask application
        Session: SQLAlchemy session factory
        graph_analyzer: GraphAnalyzer instance
        recommendation_engine: RecommendationEngine instance
        search_engine: AdvancedSearchEngine instance
    """
    app.register_blueprint(bob_ai_phase2_bp)
    app.config['BOB_AI_SESSION'] = Session
    app.config['BOB_AI_GRAPH_ANALYZER'] = graph_analyzer
    app.config['BOB_AI_RECOMMENDATION_ENGINE'] = recommendation_engine
    app.config['BOB_AI_SEARCH_ENGINE'] = search_engine

    logger.info("✅ BOB AI Expansion Phase 2 API initialized")
