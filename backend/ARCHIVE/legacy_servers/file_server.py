"""
Simple File Server for ORFEAS Frontend
Serves the HTML files and handles CORS for local development
"""

from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
import os
from pathlib import Path

app = Flask(__name__)
CORS(app, origins=["*"])

# Base directory containing our HTML files
BASE_DIR = Path(__file__).parent.parent

@app.route('/')
def home():
    """Serve the main ORFEAS portal"""
    return send_file(BASE_DIR / 'ORFEAS_MAKERS_PORTAL.html')

@app.route('/studio')
def studio():
    """Serve the ORFEAS studio"""
    return send_file(BASE_DIR / 'orfeas-studio.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(BASE_DIR, filename)

if __name__ == '__main__':
    print(f"Serving files from: {BASE_DIR}")
    print("Available routes:")
    print("  http://localhost:3000/ - ORFEAS Portal")
    print("  http://localhost:3000/studio - ORFEAS Studio")
    app.run(host='0.0.0.0', port=3000, debug=True)
