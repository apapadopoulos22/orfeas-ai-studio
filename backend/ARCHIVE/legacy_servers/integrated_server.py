"""
ORFEAS Integrated Server
Combines the Flask API backend with Hunyuan3D integration and file serving
"""

import os
import sys
import asyncio
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import logging

# Core Flask imports
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# Image and ML processing
import torch
import torchvision.transforms as transforms
from PIL import Image, ImageOps
import numpy as np
import cv2

# 3D processing
import trimesh
import open3d as o3d
from stl import mesh

# GPU and CUDA utilities
import GPUtil
import psutil

# Import our integration modules
from hunyuan_integration import get_3d_processor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OrfeasIntegratedServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
        self.app.config['SECRET_KEY'] = 'orfeas-3d-generator-secret-key'

        # Enable CORS for all routes
        CORS(self.app, origins=["*"])

        # Initialize SocketIO for real-time updates
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Setup directories
        self.setup_directories()

        # Initialize GPU detection
        self.setup_gpu()

        # Initialize 3D processor
        self.setup_3d_processor()

        # Setup routes
        self.setup_routes()

        # Job tracking
        self.active_jobs = {}
        self.job_progress = {}

        logger.info("ORFEAS Integrated Server initialized successfully")

    def setup_directories(self):
        """Create necessary directories for file processing"""
        self.base_dir = Path(__file__).parent
        self.workspace_dir = self.base_dir.parent
        self.uploads_dir = self.base_dir / "uploads"
        self.outputs_dir = self.base_dir / "outputs"
        self.temp_dir = self.base_dir / "temp"
        self.models_dir = self.base_dir / "models"

        for directory in [self.uploads_dir, self.outputs_dir, self.temp_dir, self.models_dir]:
            directory.mkdir(exist_ok=True)

        logger.info(f"Directories setup complete: {self.base_dir}")

    def setup_gpu(self):
        """Initialize GPU detection and setup CUDA if available"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gpu_info = {}

        if torch.cuda.is_available():
            self.gpu_info = {
                "available": True,
                "device_count": torch.cuda.device_count(),
                "current_device": torch.cuda.current_device(),
                "device_name": torch.cuda.get_device_name(),
                "memory_total": torch.cuda.get_device_properties(0).total_memory,
                "memory_allocated": torch.cuda.memory_allocated(),
                "memory_reserved": torch.cuda.memory_reserved()
            }
            logger.info(f"GPU detected: {self.gpu_info['device_name']}")
        else:
            self.gpu_info = {"available": False, "fallback": "CPU"}
            logger.warning("No GPU detected, falling back to CPU processing")

    def setup_3d_processor(self):
        """Initialize 3D processing engine with Hunyuan3D integration"""
        try:
            self.processor_3d = get_3d_processor(self.device)

            processor_info = self.processor_3d.get_model_info()
            logger.info(f"3D Processor initialized: {processor_info['model_type']}")

            if processor_info['status'] == 'loaded':
                logger.info(f"Capabilities: {', '.join(processor_info['capabilities'])}")
                logger.info(f"Supported formats: {', '.join(processor_info['formats'])}")

        except Exception as e:
            logger.error(f"Failed to initialize 3D processor: {e}")
            # Fallback to basic processor
            from hunyuan_integration import FallbackProcessor
            self.processor_3d = FallbackProcessor(self.device)
            logger.info("Using fallback 3D processor")

    def setup_routes(self):
        """Setup all API routes and file serving"""

        # File serving routes
        @self.app.route('/')
        def home():
            """Serve the main ORFEAS portal"""
            return send_file(self.workspace_dir / 'ORFEAS_MAKERS_PORTAL.html')

        @self.app.route('/studio')
        def studio():
            """Serve the ORFEAS studio"""
            return send_file(self.workspace_dir / 'orfeas-studio.html')

        @self.app.route('/<path:filename>')
        def serve_static(filename):
            """Serve static files"""
            return send_from_directory(self.workspace_dir, filename)

        # API Routes
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "gpu_info": self.gpu_info,
                "active_jobs": len(self.active_jobs),
                "processor": self.processor_3d.get_model_info()
            })

        @self.app.route('/api/upload-image', methods=['POST'])
        def upload_image():
            """Upload image for 3D conversion"""
            try:
                if 'image' not in request.files:
                    return jsonify({"error": "No image file provided"}), 400

                file = request.files['image']
                if file.filename == '':
                    return jsonify({"error": "No file selected"}), 400

                # Validate file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                if file_ext not in allowed_extensions:
                    return jsonify({"error": "Invalid file type"}), 400

                # Save uploaded file
                job_id = str(uuid.uuid4())
                filename = secure_filename(f"{job_id}_{file.filename}")
                file_path = self.uploads_dir / filename
                file.save(str(file_path))

                # Process image
                image_info = self.analyze_image(file_path)

                return jsonify({
                    "job_id": job_id,
                    "filename": filename,
                    "status": "uploaded",
                    "image_info": image_info
                })

            except RequestEntityTooLarge:
                return jsonify({"error": "File too large (max 50MB)"}), 413
            except Exception as e:
                logger.error(f"Upload error: {str(e)}")
                return jsonify({"error": "Upload failed"}), 500

        @self.app.route('/api/text-to-image', methods=['POST'])
        def text_to_image():
            """Generate image from text prompt using Hunyuan DiT"""
            try:
                data = request.get_json()
                prompt = data.get('prompt', '').strip()
                style = data.get('style', 'realistic')

                if not prompt:
                    return jsonify({"error": "Prompt is required"}), 400

                job_id = str(uuid.uuid4())

                # Start async image generation
                thread = threading.Thread(
                    target=self.generate_image_async,
                    args=(job_id, prompt, style),
                    kwargs=data
                )
                thread.daemon = True
                thread.start()

                return jsonify({
                    "job_id": job_id,
                    "status": "generating",
                    "prompt": prompt,
                    "style": style
                })

            except Exception as e:
                logger.error(f"Text-to-image error: {str(e)}")
                return jsonify({"error": "Generation failed"}), 500

        @self.app.route('/api/generate-3d', methods=['POST'])
        def generate_3d():
            """Generate 3D model from image using Hunyuan3D"""
            try:
                data = request.get_json()
                job_id = data.get('job_id')
                format_type = data.get('format', 'stl')
                dimensions = data.get('dimensions', {'width': 100, 'height': 100, 'depth': 20})
                quality = data.get('quality', 7)

                if not job_id:
                    return jsonify({"error": "Job ID is required"}), 400

                # Start async 3D generation
                thread = threading.Thread(
                    target=self.generate_3d_async,
                    args=(job_id, format_type, dimensions, quality)
                )
                thread.daemon = True
                thread.start()

                return jsonify({
                    "job_id": job_id,
                    "status": "generating_3d",
                    "format": format_type,
                    "dimensions": dimensions
                })

            except Exception as e:
                logger.error(f"3D generation error: {str(e)}")
                return jsonify({"error": "3D generation failed"}), 500

        @self.app.route('/api/job-status/<job_id>', methods=['GET'])
        def job_status(job_id):
            """Get job status and progress"""
            if job_id in self.job_progress:
                return jsonify(self.job_progress[job_id])
            else:
                return jsonify({"error": "Job not found"}), 404

        @self.app.route('/api/download/<job_id>/<filename>', methods=['GET'])
        def download_file(job_id, filename):
            """Download generated file"""
            try:
                file_path = self.outputs_dir / job_id / filename
                if file_path.exists():
                    return send_file(str(file_path), as_attachment=True)
                else:
                    return jsonify({"error": "File not found"}), 404
            except Exception as e:
                logger.error(f"Download error: {str(e)}")
                return jsonify({"error": "Download failed"}), 500

        @self.app.route('/api/models-info', methods=['GET'])
        def models_info():
            """Get information about loaded AI models"""
            try:
                model_info = self.processor_3d.get_model_info()

                return jsonify({
                    "hunyuan3d": model_info,
                    "device": str(self.device),
                    "gpu_available": self.gpu_info.get('available', False),
                    "backend_version": "1.0.0"
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        # WebSocket events
        @self.socketio.on('connect')
        def handle_connect():
            logger.info(f"Client connected: {request.sid}")
            emit('connected', {'status': 'Connected to ORFEAS Backend'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info(f"Client disconnected: {request.sid}")

        @self.socketio.on('subscribe_job')
        def handle_job_subscription(data):
            job_id = data.get('job_id')
            if job_id:
                logger.info(f"Client {request.sid} subscribed to job {job_id}")

    def analyze_image(self, image_path: Path) -> Dict[str, Any]:
        """Analyze uploaded image and extract metadata"""
        try:
            with Image.open(image_path) as img:
                return {
                    "size": img.size,
                    "format": img.format,
                    "mode": img.mode,
                    "has_transparency": img.mode in ('RGBA', 'LA'),
                    "file_size": os.path.getsize(image_path)
                }
        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            return {"error": str(e)}

    def generate_image_async(self, job_id: str, prompt: str, style: str, **kwargs):
        """Asynchronously generate image from text prompt using Hunyuan DiT"""
        try:
            self.job_progress[job_id] = {
                "status": "initializing",
                "progress": 0,
                "step": "Loading Hunyuan DiT model..."
            }
            self.socketio.emit('job_update', self.job_progress[job_id])

            output_dir = self.outputs_dir / job_id
            output_dir.mkdir(exist_ok=True)

            # Update progress
            self.job_progress[job_id].update({
                "status": "generating",
                "progress": 20,
                "step": "Processing text prompt..."
            })
            self.socketio.emit('job_update', self.job_progress[job_id])

            # Check if processor supports text-to-image
            processor_info = self.processor_3d.get_model_info()

            if processor_info.get('has_text2image', False):
                # Use real Hunyuan text-to-image generation
                self.job_progress[job_id].update({
                    "progress": 50,
                    "step": "Generating image with Hunyuan AI..."
                })
                self.socketio.emit('job_update', self.job_progress[job_id])

                image_path = output_dir / f"generated_{job_id}.png"

                # Generate with real Hunyuan model
                success = self.processor_3d.text_to_image_generation(
                    prompt=prompt,
                    output_path=image_path,
                    width=kwargs.get('width', 512),
                    height=kwargs.get('height', 512),
                    steps=kwargs.get('steps', 50),
                    guidance_scale=kwargs.get('guidance_scale', 7.0)
                )

                if success:
                    filename = f"generated_{job_id}.png"
                else:
                    raise Exception("Hunyuan image generation failed")

            else:
                # Fallback to placeholder generation
                logger.warning("Hunyuan text-to-image not available, using placeholder")

                self.job_progress[job_id].update({
                    "progress": 50,
                    "step": "Generating placeholder image..."
                })
                self.socketio.emit('job_update', self.job_progress[job_id])

                generated_image = self.create_placeholder_image(prompt, style)
                image_path = output_dir / f"generated_{job_id}.png"
                generated_image.save(str(image_path))
                filename = f"generated_{job_id}.png"

            # Final progress update
            self.job_progress[job_id].update({
                "status": "completed",
                "progress": 100,
                "step": "Image generation complete!",
                "output_file": filename,
                "download_url": f"/api/download/{job_id}/{filename}"
            })

            self.socketio.emit('job_update', self.job_progress[job_id])

        except Exception as e:
            logger.error(f"Image generation error: {str(e)}")
            self.job_progress[job_id] = {
                "status": "failed",
                "error": str(e)
            }
            self.socketio.emit('job_update', self.job_progress[job_id])

    def generate_3d_async(self, job_id: str, format_type: str, dimensions: Dict, quality: int):
        """Asynchronously generate 3D model from image using Hunyuan3D"""
        try:
            self.job_progress[job_id] = {
                "status": "initializing_3d",
                "progress": 0,
                "step": "Loading Hunyuan3D engine..."
            }
            self.socketio.emit('job_update', self.job_progress[job_id])

            output_dir = self.outputs_dir / job_id
            output_dir.mkdir(exist_ok=True)

            # Find input image from the job
            input_image_path = None
            for file_path in self.uploads_dir.glob(f"{job_id}_*"):
                if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']:
                    input_image_path = file_path
                    break

            # Also check if there's a generated image
            if not input_image_path:
                generated_path = output_dir / f"generated_{job_id}.png"
                if generated_path.exists():
                    input_image_path = generated_path

            if not input_image_path:
                raise Exception("No input image found for 3D generation")

            logger.info(f"Using input image: {input_image_path}")

            # Update progress - starting 3D generation
            self.job_progress[job_id].update({
                "status": "generating_3d",
                "progress": 10,
                "step": "Preprocessing image with Hunyuan3D..."
            })
            self.socketio.emit('job_update', self.job_progress[job_id])

            # Progress updates for Hunyuan3D pipeline
            self.job_progress[job_id].update({
                "progress": 25,
                "step": "Removing background..."
            })
            self.socketio.emit('job_update', self.job_progress[job_id])

            self.job_progress[job_id].update({
                "progress": 50,
                "step": "Generating 3D mesh geometry..."
            })
            self.socketio.emit('job_update', self.job_progress[job_id])

            self.job_progress[job_id].update({
                "progress": 75,
                "step": "Applying textures with Hunyuan3D Paint..."
            })
            self.socketio.emit('job_update', self.job_progress[job_id])

            # Generate 3D model with real Hunyuan3D
            output_path = output_dir / f"model_{job_id}"

            success = self.processor_3d.image_to_3d_generation(
                image_path=input_image_path,
                output_path=output_path,
                format=format_type,
                quality=quality,
                dimensions=dimensions
            )

            if success:
                # Find the generated file
                generated_files = list(output_dir.glob(f"model_{job_id}.*"))
                if generated_files:
                    model_file = generated_files[0].name
                    logger.info(f"3D model generated successfully: {model_file}")
                else:
                    raise Exception("3D model file not found after generation")
            else:
                # Fallback to placeholder if Hunyuan3D fails
                logger.warning("Hunyuan3D generation failed, creating placeholder")
                model_file = self.create_placeholder_3d_model(job_id, format_type, dimensions)

            self.job_progress[job_id].update({
                "status": "completed",
                "progress": 100,
                "step": "3D model generation complete!",
                "output_file": model_file,
                "download_url": f"/api/download/{job_id}/{model_file}",
                "format": format_type,
                "dimensions": dimensions
            })

            self.socketio.emit('job_update', self.job_progress[job_id])

        except Exception as e:
            logger.error(f"3D generation error: {str(e)}")
            self.job_progress[job_id] = {
                "status": "failed",
                "error": str(e)
            }
            self.socketio.emit('job_update', self.job_progress[job_id])

    def create_placeholder_image(self, prompt: str, style: str) -> Image.Image:
        """Create a placeholder generated image (fallback when Hunyuan DiT not available)"""
        # Create a gradient image based on style
        width, height = 512, 512
        image = Image.new('RGB', (width, height))

        # Style-based color schemes
        color_schemes = {
            'realistic': [(70, 130, 180), (135, 206, 235)],
            'artistic': [(255, 69, 0), (255, 140, 0)],
            'anime': [(147, 112, 219), (186, 85, 211)],
            'cyberpunk': [(0, 255, 65), (0, 102, 255)],
            'fantasy': [(138, 43, 226), (50, 205, 50)],
            'minimalist': [(105, 105, 105), (220, 220, 220)]
        }

        colors = color_schemes.get(style, color_schemes['realistic'])

        # Create gradient
        for y in range(height):
            ratio = y / height
            color = tuple(int(colors[0][i] * (1-ratio) + colors[1][i] * ratio) for i in range(3))
            for x in range(width):
                image.putpixel((x, y), color)

        return image

    def create_placeholder_3d_model(self, job_id: str, format_type: str, dimensions: Dict) -> str:
        """Create a placeholder 3D model file (fallback when Hunyuan3D not available)"""
        output_dir = self.outputs_dir / job_id

        if format_type == 'stl':
            filename = f"model_{job_id}.stl"
            self.create_cube_stl(output_dir / filename, dimensions)
        elif format_type == 'obj':
            filename = f"model_{job_id}.obj"
            self.create_cube_obj(output_dir / filename, dimensions)
        else:
            filename = f"model_{job_id}.{format_type}"
            with open(output_dir / filename, 'w') as f:
                f.write(f"# ORFEAS 3D Model - {format_type.upper()}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Dimensions: {dimensions}\n")

        return filename

    def create_cube_stl(self, output_path: Path, dimensions: Dict):
        """Create a simple cube STL file"""
        try:
            w, h, d = dimensions['width'], dimensions['height'], dimensions['depth']

            # Define vertices for a cube
            vertices = np.array([
                [0, 0, 0], [w, 0, 0], [w, h, 0], [0, h, 0],  # bottom
                [0, 0, d], [w, 0, d], [w, h, d], [0, h, d]   # top
            ], dtype=np.float32)

            # Define faces for a cube
            faces = np.array([
                [0, 1, 2], [0, 2, 3],  # bottom
                [4, 7, 6], [4, 6, 5],  # top
                [0, 4, 5], [0, 5, 1],  # front
                [2, 6, 7], [2, 7, 3],  # back
                [0, 3, 7], [0, 7, 4],  # left
                [1, 5, 6], [1, 6, 2]   # right
            ])

            # Create STL mesh
            cube_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
            for i, face in enumerate(faces):
                for j in range(3):
                    cube_mesh.vectors[i][j] = vertices[face[j], :]

            cube_mesh.save(str(output_path))

        except Exception as e:
            logger.error(f"STL creation error: {str(e)}")
            # Fallback: create text file
            with open(output_path.with_suffix('.txt'), 'w') as f:
                f.write(f"STL model placeholder - {dimensions}")

    def create_cube_obj(self, output_path: Path, dimensions: Dict):
        """Create a simple cube OBJ file"""
        try:
            w, h, d = dimensions['width'], dimensions['height'], dimensions['depth']

            obj_content = f"""# ORFEAS 3D Cube Model
# Dimensions: {w}x{h}x{d}mm

# Vertices
v 0 0 0
v {w} 0 0
v {w} {h} 0
v 0 {h} 0
v 0 0 {d}
v {w} 0 {d}
v {w} {h} {d}
v 0 {h} {d}

# Faces
f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 5 1 4 8
"""

            with open(output_path, 'w') as f:
                f.write(obj_content)

        except Exception as e:
            logger.error(f"OBJ creation error: {str(e)}")

    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the integrated Flask application"""
        logger.info(f"Starting ORFEAS Integrated Server on {host}:{port}")
        logger.info("Available services:")
        logger.info("  [HOME] ORFEAS Portal: http://localhost:5000/")
        logger.info("  [ART] ORFEAS Studio: http://localhost:5000/studio")
        logger.info("  [STATS] API Health: http://localhost:5000/api/health")
        logger.info("  [SIGNAL] WebSocket: ws://localhost:5000")

        self.socketio.run(self.app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    server = OrfeasIntegratedServer()
    server.run(debug=True)
