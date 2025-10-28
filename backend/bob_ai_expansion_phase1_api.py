"""
BOB AI Expansion - Phase 1: REST API Endpoints
===============================================

15+ Flask endpoints for managing 100 categories, 500 disciplines,
and 800+ library mappings.

Integration with existing ORFEAS main.py Flask application

Author: ORFEAS AI - BOB AI Expansion v10.0
Date: October 28, 2025
"""

import logging
from typing import Dict, List, Optional, Any
from functools import wraps
from datetime import datetime

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

# Import database models
from bob_ai_expansion_phase1_database import (
    ExpandedCategory, ExpandedDiscipline, LibraryMapping,
    DisciplineLink, LearningPath, ExpandedKnowledgeLoader
)

logger = logging.getLogger(__name__)

# Create Blueprint for BOB AI Expansion routes
bob_ai_expansion_bp = Blueprint(
    'bob_ai_expansion',
    __name__,
    url_prefix='/api/v2'
)


# ============================================================================
# Helper Functions & Decorators
# ============================================================================

def require_session(f):
    """Decorator to inject database session"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        Session = current_app.config.get('BOB_AI_SESSION')
        if not Session:
            return jsonify({'error': 'Database session not configured'}), 500

        session = Session()
        try:
            kwargs['session'] = session
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()

    return decorated_function


def serialize_category(category: ExpandedCategory) -> Dict:
    """Convert category model to JSON"""
    return {
        'id': category.id,
        'name': category.name,
        'tier': category.tier,
        'tier_name': category.tier_name,
        'description': category.description,
        'disciplines_count': category.disciplines_count,
        'libraries_count': category.libraries_count,
        'keywords': category.keywords,
        'maturity_level': category.maturity_level,
        'created_at': category.created_at.isoformat() if category.created_at else None,
    }


def serialize_discipline(discipline: ExpandedDiscipline) -> Dict:
    """Convert discipline model to JSON"""
    return {
        'id': discipline.id,
        'name': discipline.name,
        'category_id': discipline.category_id,
        'description': discipline.description,
        'difficulty_level': discipline.difficulty_level,
        'estimated_hours': discipline.estimated_hours,
        'use_cases': discipline.use_cases,
        'topics': discipline.topics,
        'keywords': discipline.keywords,
        'estimated_hours': discipline.estimated_hours,
        'certification_available': discipline.certification_available,
        'status': discipline.status,
        'created_at': discipline.created_at.isoformat() if discipline.created_at else None,
    }


def serialize_library(library: LibraryMapping) -> Dict:
    """Convert library model to JSON"""
    return {
        'id': library.id,
        'library_name': library.library_name,
        'package_name': library.package_name,
        'language': library.language,
        'version': library.version,
        'description': library.description,
        'install_command': library.install_command,
        'import_statement': library.import_statement,
        'documentation_url': library.documentation_url,
        'github_url': library.github_url,
        'relevance_score': library.relevance_score,
        'technology_stack': library.technology_stack,
        'is_primary': library.is_primary,
        'maturity_status': library.maturity_status,
    }


# ============================================================================
# Categories Endpoints
# ============================================================================

@bob_ai_expansion_bp.route('/categories/expanded', methods=['GET'])
@require_session
def get_all_categories(session: Session):
    """
    GET /api/v2/categories/expanded

    Get all 100+ expanded categories with filtering and pagination

    Query Parameters:
      - page: Page number (default: 1)
      - per_page: Items per page (default: 20)
      - tier: Filter by tier (1-8)
      - maturity: Filter by maturity level
      - search: Search in name/description

    Response:
      {
        "categories": [{...}, ...],
        "total": 115,
        "page": 1,
        "per_page": 20,
        "total_pages": 6
      }
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        tier = request.args.get('tier', None, type=int)
        maturity = request.args.get('maturity', None, type=str)
        search = request.args.get('search', None, type=str)

        # Build query
        query = session.query(ExpandedCategory)

        # Apply filters
        if tier:
            query = query.filter_by(tier=tier)
        if maturity:
            query = query.filter_by(maturity_level=maturity)
        if search:
            query = query.filter(
                or_(
                    ExpandedCategory.name.ilike(f'%{search}%'),
                    ExpandedCategory.description.ilike(f'%{search}%')
                )
            )

        # Get total
        total = query.count()

        # Paginate
        categories = query.offset((page - 1) * per_page).limit(per_page).all()

        return jsonify({
            'categories': [serialize_category(c) for c in categories],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }), 200

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({'error': str(e)}), 500


@bob_ai_expansion_bp.route('/categories/<int:category_id>', methods=['GET'])
@require_session
def get_category(category_id: int, session: Session):
    """
    GET /api/v2/categories/<id>

    Get single category with all disciplines and libraries
    """
    try:
        category = session.query(ExpandedCategory).filter_by(id=category_id).first()

        if not category:
            return jsonify({'error': 'Category not found'}), 404

        result = serialize_category(category)
        result['disciplines'] = [
            serialize_discipline(d) for d in category.disciplines
        ]

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error getting category: {e}")
        return jsonify({'error': str(e)}), 500


@bob_ai_expansion_bp.route('/categories/<int:category_id>/disciplines', methods=['GET'])
@require_session
def get_category_disciplines(category_id: int, session: Session):
    """
    GET /api/v2/categories/<id>/disciplines

    Get all disciplines in a category

    Query Parameters:
      - difficulty: Filter by difficulty level
      - status: Filter by status
    """
    try:
        category = session.query(ExpandedCategory).filter_by(id=category_id).first()

        if not category:
            return jsonify({'error': 'Category not found'}), 404

        query = session.query(ExpandedDiscipline).filter_by(category_id=category_id)

        # Apply filters
        difficulty = request.args.get('difficulty', None, type=str)
        status = request.args.get('status', None, type=str)

        if difficulty:
            query = query.filter_by(difficulty_level=difficulty)
        if status:
            query = query.filter_by(status=status)

        disciplines = query.all()

        return jsonify({
            'category': serialize_category(category),
            'disciplines': [serialize_discipline(d) for d in disciplines],
            'total': len(disciplines)
        }), 200

    except Exception as e:
        logger.error(f"Error getting category disciplines: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Disciplines Endpoints
# ============================================================================

@bob_ai_expansion_bp.route('/disciplines/expanded', methods=['GET'])
@require_session
def get_all_disciplines(session: Session):
    """
    GET /api/v2/disciplines/expanded

    Get all 500+ expanded disciplines

    Query Parameters:
      - page: Page number
      - per_page: Items per page
      - category: Filter by category ID
      - difficulty: Filter by difficulty level (beginner, intermediate, advanced, expert)
      - status: Filter by status
      - search: Search in name/description/keywords

    Response:
      {
        "disciplines": [{...}, ...],
        "total": 891,
        "page": 1,
        "per_page": 20
      }
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category_id = request.args.get('category', None, type=int)
        difficulty = request.args.get('difficulty', None, type=str)
        status = request.args.get('status', None, type=str)
        search = request.args.get('search', None, type=str)

        # Build query
        query = session.query(ExpandedDiscipline)

        # Apply filters
        if category_id:
            query = query.filter_by(category_id=category_id)
        if difficulty:
            query = query.filter_by(difficulty_level=difficulty)
        if status:
            query = query.filter_by(status=status)
        if search:
            query = query.filter(
                or_(
                    ExpandedDiscipline.name.ilike(f'%{search}%'),
                    ExpandedDiscipline.description.ilike(f'%{search}%'),
                    ExpandedDiscipline.keywords.contains([search])
                )
            )

        total = query.count()
        disciplines = query.offset((page - 1) * per_page).limit(per_page).all()

        return jsonify({
            'disciplines': [serialize_discipline(d) for d in disciplines],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }), 200

    except Exception as e:
        logger.error(f"Error getting disciplines: {e}")
        return jsonify({'error': str(e)}), 500


@bob_ai_expansion_bp.route('/disciplines/<int:discipline_id>', methods=['GET'])
@require_session
def get_discipline(discipline_id: int, session: Session):
    """
    GET /api/v2/disciplines/<id>

    Get single discipline with all libraries and relationships
    """
    try:
        discipline = session.query(ExpandedDiscipline).filter_by(id=discipline_id).first()

        if not discipline:
            return jsonify({'error': 'Discipline not found'}), 404

        result = serialize_discipline(discipline)

        # Add libraries
        result['libraries'] = [
            serialize_library(lib) for lib in discipline.libraries
        ]

        # Add prerequisites
        if discipline.prerequisite_disciplines:
            prerequisites = session.query(ExpandedDiscipline).filter(
                ExpandedDiscipline.id.in_(discipline.prerequisite_disciplines)
            ).all()
            result['prerequisites'] = [serialize_discipline(p) for p in prerequisites]

        # Add related disciplines
        if discipline.related_disciplines:
            related = session.query(ExpandedDiscipline).filter(
                ExpandedDiscipline.id.in_(discipline.related_disciplines)
            ).all()
            result['related'] = [serialize_discipline(r) for r in related]

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error getting discipline: {e}")
        return jsonify({'error': str(e)}), 500


@bob_ai_expansion_bp.route('/disciplines/search', methods=['POST'])
@require_session
def search_disciplines(session: Session):
    """
    POST /api/v2/disciplines/search

    Advanced search for disciplines

    Request Body:
      {
        "query": "quantum",
        "difficulty": "advanced",
        "category_id": 5,
        "limit": 50
      }

    Response:
      {
        "results": [{...}, ...],
        "count": 12,
        "query_time_ms": 45
      }
    """
    try:
        import time
        start_time = time.time()

        data = request.get_json() or {}
        query_str = data.get('query', '')
        difficulty = data.get('difficulty')
        category_id = data.get('category_id')
        limit = data.get('limit', 50)

        query = session.query(ExpandedDiscipline)

        if query_str:
            query = query.filter(
                or_(
                    ExpandedDiscipline.name.ilike(f'%{query_str}%'),
                    ExpandedDiscipline.description.ilike(f'%{query_str}%'),
                    ExpandedDiscipline.topics.contains([query_str])
                )
            )

        if difficulty:
            query = query.filter_by(difficulty_level=difficulty)

        if category_id:
            query = query.filter_by(category_id=category_id)

        results = query.limit(limit).all()

        elapsed = (time.time() - start_time) * 1000

        return jsonify({
            'results': [serialize_discipline(d) for d in results],
            'count': len(results),
            'query_time_ms': int(elapsed)
        }), 200

    except Exception as e:
        logger.error(f"Error searching disciplines: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Libraries Endpoints
# ============================================================================

@bob_ai_expansion_bp.route('/libraries', methods=['GET'])
@require_session
def get_all_libraries(session: Session):
    """
    GET /api/v2/libraries

    Get all 800+ library mappings

    Query Parameters:
      - page: Page number
      - per_page: Items per page
      - discipline_id: Filter by discipline
      - language: Filter by language (python, javascript, etc.)
      - technology_stack: Filter by tech stack
      - search: Search in library name/description
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        discipline_id = request.args.get('discipline_id', None, type=int)
        language = request.args.get('language', None, type=str)
        tech_stack = request.args.get('technology_stack', None, type=str)
        search = request.args.get('search', None, type=str)

        query = session.query(LibraryMapping)

        if discipline_id:
            query = query.filter_by(discipline_id=discipline_id)
        if language:
            query = query.filter_by(language=language)
        if tech_stack:
            query = query.filter_by(technology_stack=tech_stack)
        if search:
            query = query.filter(
                or_(
                    LibraryMapping.library_name.ilike(f'%{search}%'),
                    LibraryMapping.description.ilike(f'%{search}%')
                )
            )

        total = query.count()
        libraries = query.offset((page - 1) * per_page).limit(per_page).all()

        return jsonify({
            'libraries': [serialize_library(lib) for lib in libraries],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }), 200

    except Exception as e:
        logger.error(f"Error getting libraries: {e}")
        return jsonify({'error': str(e)}), 500


@bob_ai_expansion_bp.route('/libraries/search', methods=['POST'])
@require_session
def search_libraries(session: Session):
    """
    POST /api/v2/libraries/search

    Search for libraries

    Request Body:
      {
        "query": "pytorch",
        "language": "python",
        "technology_stack": "Deep Learning",
        "limit": 100
      }
    """
    try:
        data = request.get_json() or {}
        query_str = data.get('query', '')
        language = data.get('language')
        tech_stack = data.get('technology_stack')
        limit = data.get('limit', 100)

        query = session.query(LibraryMapping)

        if query_str:
            query = query.filter(
                or_(
                    LibraryMapping.library_name.ilike(f'%{query_str}%'),
                    LibraryMapping.package_name.ilike(f'%{query_str}%'),
                    LibraryMapping.description.ilike(f'%{query_str}%')
                )
            )

        if language:
            query = query.filter_by(language=language)

        if tech_stack:
            query = query.filter_by(technology_stack=tech_stack)

        results = query.limit(limit).all()

        return jsonify({
            'results': [serialize_library(lib) for lib in results],
            'count': len(results)
        }), 200

    except Exception as e:
        logger.error(f"Error searching libraries: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Learning Paths Endpoints
# ============================================================================

@bob_ai_expansion_bp.route('/learning-paths', methods=['GET'])
@require_session
def get_learning_paths(session: Session):
    """
    GET /api/v2/learning-paths

    Get all learning paths

    Query Parameters:
      - skill_level: Filter by skill level
      - industry: Filter by industry
      - search: Search in name/description
    """
    try:
        skill_level = request.args.get('skill_level', None, type=str)
        industry = request.args.get('industry', None, type=str)
        search = request.args.get('search', None, type=str)

        query = session.query(LearningPath).filter_by(is_published=True)

        if skill_level:
            query = query.filter_by(skill_level=skill_level)
        if industry:
            query = query.filter_by(industry_focus=industry)
        if search:
            query = query.filter(
                or_(
                    LearningPath.name.ilike(f'%{search}%'),
                    LearningPath.description.ilike(f'%{search}%')
                )
            )

        paths = query.all()

        return jsonify({
            'paths': [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'skill_level': p.skill_level,
                    'duration_weeks': p.estimated_duration_weeks,
                    'target_role': p.target_role,
                    'discipline_count': len(p.discipline_ids),
                    'library_count': len(p.library_ids)
                }
                for p in paths
            ],
            'total': len(paths)
        }), 200

    except Exception as e:
        logger.error(f"Error getting learning paths: {e}")
        return jsonify({'error': str(e)}), 500


@bob_ai_expansion_bp.route('/learning-paths/<int:path_id>', methods=['GET'])
@require_session
def get_learning_path(path_id: int, session: Session):
    """
    GET /api/v2/learning-paths/<id>

    Get single learning path with all disciplines and libraries
    """
    try:
        path = session.query(LearningPath).filter_by(id=path_id).first()

        if not path:
            return jsonify({'error': 'Learning path not found'}), 404

        # Get disciplines
        disciplines = session.query(ExpandedDiscipline).filter(
            ExpandedDiscipline.id.in_(path.discipline_ids)
        ).all()

        # Get libraries
        libraries = session.query(LibraryMapping).filter(
            LibraryMapping.id.in_(path.library_ids)
        ).all()

        return jsonify({
            'id': path.id,
            'name': path.name,
            'description': path.description,
            'skill_level': path.skill_level,
            'duration_weeks': path.estimated_duration_weeks,
            'target_role': path.target_role,
            'industry_focus': path.industry_focus,
            'outcomes': path.outcomes,
            'prerequisites_text': path.prerequisites_text,
            'disciplines': [serialize_discipline(d) for d in disciplines],
            'libraries': [serialize_library(lib) for lib in libraries],
            'projects': path.projects,
            'certifications': path.certifications
        }), 200

    except Exception as e:
        logger.error(f"Error getting learning path: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Statistics & Health Check Endpoints
# ============================================================================

@bob_ai_expansion_bp.route('/statistics', methods=['GET'])
@require_session
def get_statistics(session: Session):
    """
    GET /api/v2/statistics

    Get BOB AI expansion statistics
    """
    try:
        stats = {
            'categories': session.query(ExpandedCategory).count(),
            'disciplines': session.query(ExpandedDiscipline).count(),
            'libraries': session.query(LibraryMapping).count(),
            'learning_paths': session.query(LearningPath).filter_by(is_published=True).count(),
            'categories_by_tier': {},
            'disciplines_by_difficulty': {},
            'libraries_by_language': {}
        }

        # Count by tier
        for tier in range(1, 9):
            count = session.query(ExpandedCategory).filter_by(tier=tier).count()
            if count > 0:
                stats['categories_by_tier'][f'tier_{tier}'] = count

        # Count by difficulty
        for difficulty in ['beginner', 'intermediate', 'advanced', 'expert']:
            count = session.query(ExpandedDiscipline).filter_by(
                difficulty_level=difficulty
            ).count()
            if count > 0:
                stats['disciplines_by_difficulty'][difficulty] = count

        # Count by language
        for language in ['python', 'javascript', 'julia', 'rust', 'cpp']:
            count = session.query(LibraryMapping).filter_by(language=language).count()
            if count > 0:
                stats['libraries_by_language'][language] = count

        return jsonify(stats), 200

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({'error': str(e)}), 500


@bob_ai_expansion_bp.route('/health', methods=['GET'])
def health_check():
    """
    GET /api/v2/health

    Health check for BOB AI expansion service
    """
    return jsonify({
        'status': 'healthy',
        'service': 'BOB AI Expansion v10.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# ============================================================================
# Integration with Flask Application
# ============================================================================

def init_bob_ai_expansion_api(app, Session):
    """
    Initialize BOB AI expansion API with Flask app

    Args:
        app: Flask application instance
        Session: SQLAlchemy session factory

    Example:
        from flask import Flask
        from sqlalchemy.orm import sessionmaker

        app = Flask(__name__)
        Session = sessionmaker(bind=engine)
        init_bob_ai_expansion_api(app, Session)
    """
    # Register blueprint
    app.register_blueprint(bob_ai_expansion_bp)

    # Store session factory in app config
    app.config['BOB_AI_SESSION'] = Session

    logger.info("✅ BOB AI Expansion API initialized with 15+ endpoints")
    logger.info("   Available at: /api/v2/")
    logger.info("   - GET /categories/expanded")
    logger.info("   - GET /disciplines/expanded")
    logger.info("   - GET /libraries")
    logger.info("   - GET /learning-paths")
    logger.info("   - POST /disciplines/search")
    logger.info("   - POST /libraries/search")
    logger.info("   - GET /statistics")


if __name__ == '__main__':
    print("BOB AI Expansion - Phase 1: API Endpoints")
    print("=" * 50)
    print("This module should be imported and initialized in main.py")
    print("\nExample integration in main.py:")
    print("  from bob_ai_expansion_phase1_api import init_bob_ai_expansion_api")
    print("  init_bob_ai_expansion_api(app, Session)")
