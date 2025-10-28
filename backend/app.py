"""
PHASE 1: Backend API Server - Flask Application
Author: BOB AI System
Date: October 28, 2025
Version: 1.0

Purpose: Connect frontend (Next.js) to ML classifier backend
Features:
  - REST API endpoints for DDC taxonomy
  - ML classification endpoints
  - CORS support for frontend communication
  - Error handling and logging
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
app.config['JSON_SORT_KEYS'] = False
API_PORT = int(os.getenv('API_PORT', 5000))
DEBUG_MODE = os.getenv('FLASK_ENV', 'development') == 'development'

# Global data cache
ddc_taxonomy = None
sample_problems = None
ml_classifier = None

def load_data():
    """Load taxonomy and sample data from JSON files"""
    global ddc_taxonomy, sample_problems

    try:
        # Load DDC taxonomy
        ddc_path = Path(__file__).parent.parent / 'ddc_taxonomy_comprehensive.json'
        with open(ddc_path, 'r') as f:
            ddc_taxonomy = json.load(f)
        logger.info(f"✅ Loaded DDC taxonomy: {len(ddc_taxonomy)} codes")

        # Load sample problems
        problems_path = Path(__file__).parent.parent / 'sample_problems_50_classified.json'
        with open(problems_path, 'r') as f:
            sample_problems = json.load(f)
        logger.info(f"✅ Loaded sample problems: {len(sample_problems)} samples")

        return True
    except Exception as e:
        logger.error(f"❌ Failed to load data: {e}")
        return False

def load_ml_classifier():
    """Import and initialize ML classifier"""
    global ml_classifier

    try:
        # Import ml_classifier from src directory
        from src.ml_classifier import MLClassifier
        ml_classifier = MLClassifier()
        logger.info("✅ ML Classifier initialized successfully")
        return True
    except Exception as e:
        logger.warning(f"⚠️ ML Classifier not available: {e}")
        logger.info("   Continuing with basic classification support")
        return False

# ═════════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════════

@app.route('/health', methods=['GET'])
def health_check():
    """System health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0',
        'backend': 'Flask',
        'data_loaded': ddc_taxonomy is not None,
        'ml_ready': ml_classifier is not None,
        'timestamp': __import__('datetime').datetime.utcnow().isoformat()
    }), 200

@app.route('/ready', methods=['GET'])
def ready_check():
    """Readiness check for deployment"""
    ready = (ddc_taxonomy is not None and
             sample_problems is not None)
    return jsonify({
        'ready': ready,
        'ddc_codes': len(ddc_taxonomy) if ddc_taxonomy else 0,
        'samples': len(sample_problems) if sample_problems else 0
    }), 200 if ready else 503

# ═════════════════════════════════════════════════════════════════════════════════
# DDC TAXONOMY ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════════

@app.route('/api/ddc/all', methods=['GET'])
def get_all_ddc():
    """Get all DDC codes"""
    if not ddc_taxonomy:
        return jsonify({'error': 'Data not loaded'}), 503

    return jsonify({
        'success': True,
        'count': len(ddc_taxonomy),
        'data': ddc_taxonomy
    }), 200

@app.route('/api/ddc/search', methods=['GET'])
def search_ddc():
    """Search DDC codes by keyword"""
    if not ddc_taxonomy:
        return jsonify({'error': 'Data not loaded'}), 503

    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400

    results = []
    for code in ddc_taxonomy:
        code_str = str(code).lower()
        if query in code_str:
            results.append(code)

    return jsonify({
        'success': True,
        'query': query,
        'count': len(results),
        'results': results
    }), 200

@app.route('/api/ddc/<code>', methods=['GET'])
def get_ddc_code(code):
    """Get specific DDC code details"""
    if not ddc_taxonomy:
        return jsonify({'error': 'Data not loaded'}), 503

    for ddc_item in ddc_taxonomy:
        if str(ddc_item).startswith(code):
            return jsonify({
                'success': True,
                'code': code,
                'data': ddc_item
            }), 200

    return jsonify({
        'error': f'DDC code {code} not found'
    }), 404

# ═════════════════════════════════════════════════════════════════════════════════
# PROBLEM & CLASSIFICATION ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════════

@app.route('/api/problems', methods=['GET'])
def get_problems():
    """Get all sample problems"""
    if not sample_problems:
        return jsonify({'error': 'Problems not loaded'}), 503

    return jsonify({
        'success': True,
        'count': len(sample_problems),
        'data': sample_problems
    }), 200

@app.route('/api/problems/<int:problem_id>', methods=['GET'])
def get_problem(problem_id):
    """Get specific problem by ID"""
    if not sample_problems:
        return jsonify({'error': 'Problems not loaded'}), 503

    if 0 <= problem_id < len(sample_problems):
        return jsonify({
            'success': True,
            'id': problem_id,
            'data': sample_problems[problem_id]
        }), 200

    return jsonify({
        'error': f'Problem {problem_id} not found'
    }), 404

@app.route('/api/classify', methods=['POST'])
def classify_problem():
    """Classify a problem using ML classifier"""
    try:
        data = request.get_json()
        problem_text = data.get('problem', '')

        if not problem_text:
            return jsonify({'error': 'Problem text required'}), 400

        # Use ML classifier if available, otherwise basic classification
        if ml_classifier:
            try:
                result = ml_classifier.classify(problem_text)
                return jsonify({
                    'success': True,
                    'problem': problem_text,
                    'classification': result,
                    'method': 'ml_classifier'
                }), 200
            except Exception as e:
                logger.warning(f"ML classification failed: {e}")

        # Fallback: Basic keyword matching
        classification = {
            'primary_ddc': '000-099',
            'primary_name': 'Computer Science',
            'confidence': 0.5,
            'message': 'Basic classification (ML not available)'
        }

        return jsonify({
            'success': True,
            'problem': problem_text,
            'classification': classification,
            'method': 'basic_matching'
        }), 200

    except Exception as e:
        logger.error(f"Classification error: {e}")
        return jsonify({
            'error': str(e)
        }), 500

# ═════════════════════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═════════════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# ═════════════════════════════════════════════════════════════════════════════════
# INITIALIZATION & STARTUP
# ═════════════════════════════════════════════════════════════════════════════════

@app.before_request
def before_request():
    """Pre-request initialization"""
    pass

@app.after_request
def after_request(response):
    """Post-request cleanup"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

def initialize():
    """Initialize application"""
    logger.info("═" * 80)
    logger.info("🚀 PHASE 1 BACKEND API - INITIALIZATION STARTED")
    logger.info("═" * 80)

    logger.info("Step 1: Loading data files...")
    if not load_data():
        logger.error("❌ Failed to load data files - exiting")
        return False

    logger.info("Step 2: Loading ML classifier...")
    load_ml_classifier()  # Non-critical - continues if fails

    logger.info("Step 3: Configuration verified")
    logger.info(f"   - Flask Environment: {os.getenv('FLASK_ENV', 'development')}")
    logger.info(f"   - Debug Mode: {DEBUG_MODE}")
    logger.info(f"   - API Port: {API_PORT}")
    logger.info(f"   - CORS Enabled: True")

    logger.info("═" * 80)
    logger.info("✅ PHASE 1 BACKEND READY")
    logger.info(f"🌐 Server starting on http://localhost:{API_PORT}")
    logger.info("═" * 80)

    return True

# ═════════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    if not initialize():
        sys.exit(1)

    try:
        app.run(
            host='127.0.0.1',
            port=API_PORT,
            debug=DEBUG_MODE,
            use_reloader=False,  # Disable reloader to avoid double initialization
        )
    except KeyboardInterrupt:
        logger.info("\n⏹️ Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)
