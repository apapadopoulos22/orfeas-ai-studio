"""
ORFEAS AI Studio - Minimal Flask Server
Simple HTTP server for development and Docker deployment
"""

import os
import sys
from pathlib import Path
from flask import Flask, send_file, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, static_folder='..', static_url_path='')
CORS(app)

# Configure SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'ORFEAS Studio backend is running',
        'version': '1.0.0'
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Serve the main HTML file"""
    try:
        return send_file('../orfeas-ai-studio.html', mimetype='text/html')
    except:
        return jsonify({'error': 'Frontend not found'}), 404

@app.route('/api/status', methods=['GET'])
def status():
    """Return system status"""
    return jsonify({
        'status': 'running',
        'features': [
            'WebSocket support',
            'CORS enabled',
            'Health checks'
        ]
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# WebSocket connection
@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info('Client connected')
    return True

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info('Client disconnected')

if __name__ == '__main__':
    # Run server
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'

    logger.info(f"Starting ORFEAS Studio backend on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)
