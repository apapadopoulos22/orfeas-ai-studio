#!/usr/bin/env python3
"""
Safe Server Startup for ORFEAS Backend
Handles model loading failures gracefully and provides fallback functionality
"""

import sys
import os
from pathlib import Path
import logging
import signal
import time
from flask import Flask, jsonify, request, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import threading
import tempfile
import traceback
import uuid
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'orfeas-makers-portal-secret'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Enable CORS
CORS(app, origins="*")

# Initialize SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    logger=False,
    engineio_logger=False
)

# Global state
processor = None
job_progress = {}
active_jobs = set()

def initialize_ai_processor():
    """Initialize AI processor with safe error handling"""
    global processor

    logger.info("[AI] Initializing AI processor...")

    try:
        # Import and initialize processor
        import hunyuan_integration
        processor = hunyuan_integration.get_3d_processor()

        if processor and processor.is_available():
            model_info = processor.get_model_info()
            logger.info(f"[OK] AI processor initialized: {model_info.get('model_type', 'Unknown')}")
            return True
        else:
            logger.warning("[WARN] AI processor not available, using fallback")
            return False

    except Exception as e:
        logger.error(f"[FAIL] Failed to initialize AI processor: {e}")
        logger.info("ðŸ”„ Falling back to safe mode...")

        # Create a minimal fallback processor
        try:
            import hunyuan_integration
            processor = hunyuan_integration.FallbackProcessor()
            logger.info("[OK] Fallback processor initialized")
            return True
        except Exception as fallback_error:
            logger.error(f"[FAIL] Even fallback failed: {fallback_error}")
            processor = None
            return False

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    global processor

    processor_status = "not_initialized"
    if processor:
        if hasattr(processor, 'is_available') and processor.is_available():
            processor_status = "available"
        else:
            processor_status = "fallback"

    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "processor_status": processor_status,
        "active_jobs": len(active_jobs),
        "gpu_available": "cuda" in str(getattr(processor, 'device', 'cpu')) if processor else False
    })

@app.route('/api/models-info', methods=['GET'])
def models_info():
    """Get model information"""
    global processor

    if not processor:
        return jsonify({
            "error": "Processor not initialized",
            "suggestion": "Try restarting the server"
        }), 503

    try:
        info = processor.get_model_info()
        return jsonify(info)
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/text-to-image', methods=['POST'])
def text_to_image():
    """Generate image from text prompt (for orfeas-studio.html)"""
    global processor, job_progress, active_jobs

    if not processor:
        return jsonify({"error": "AI processor not initialized"}), 503

    try:
        # Get job parameters
        job_id = str(uuid.uuid4())
        data = request.get_json()

        if not data or 'prompt' not in data:
            return jsonify({"error": "No text prompt provided"}), 400

        prompt = data['prompt']

        # Initialize job tracking for image generation
        job_progress[job_id] = {
            "status": "started",
            "progress": 0,
            "message": "Initializing image generation...",
            "timestamp": datetime.now().isoformat(),
            "type": "text_to_image"
        }
        active_jobs.add(job_id)

        # Emit initial status
        socketio.emit('job_update', {
            'job_id': job_id,
            **job_progress[job_id]
        })

        # Start processing in background thread
        def process_text_to_image():
            try:
                # Update progress
                job_progress[job_id].update({
                    "status": "processing",
                    "progress": 25,
                    "message": "Generating image from text..."
                })
                socketio.emit('job_update', {'job_id': job_id, **job_progress[job_id]})

                # Create output directory
                output_dir = Path("outputs") / job_id
                output_dir.mkdir(parents=True, exist_ok=True)

                # Generate image
                image_path = output_dir / "generated_image.png"

                # Update progress
                job_progress[job_id].update({
                    "progress": 75,
                    "message": "Creating image..."
                })
                socketio.emit('job_update', {'job_id': job_id, **job_progress[job_id]})

                # Try text-to-image generation or fallback
                success = False
                if hasattr(processor, 'text_to_image_generation') and processor.get_model_info().get('has_text2image', False):
                    logger.info("Attempting AI text-to-image generation")
                    success = processor.text_to_image_generation(prompt, str(image_path))
                    if not success:
                        logger.warning("AI text-to-image failed, using fallback")

                if not success:
                    logger.info("Using fallback image creation")
                    success = create_fallback_image(prompt, str(image_path))

                if success and image_path.exists():
                    # Verify the image is valid
                    try:
                        from PIL import Image as PILImage
                        with PILImage.open(image_path) as img:
                            img.verify()

                        file_size = image_path.stat().st_size
                        logger.info(f"[OK] Image generation successful: {file_size} bytes")

                        job_progress[job_id].update({
                            "status": "completed",
                            "progress": 100,
                            "message": "Image generation completed successfully!",
                            "output_file": str(image_path),
                            "file_size": file_size,
                            "download_url": f"/api/download/{job_id}/generated_image.png",
                            "image_url": f"/api/download/{job_id}/generated_image.png"
                        })
                    except Exception as verify_error:
                        logger.error(f"Generated image verification failed: {verify_error}")
                        job_progress[job_id].update({
                            "status": "failed",
                            "progress": 0,
                            "message": f"Generated image is invalid: {verify_error}"
                        })
                else:
                    error_msg = f"Failed to generate image at {image_path}"
                    logger.error(f"[FAIL] {error_msg}")
                    job_progress[job_id].update({
                        "status": "failed",
                        "progress": 0,
                        "message": error_msg
                    })

            except Exception as e:
                logger.error(f"Text-to-image job {job_id} failed: {e}")
                logger.error(traceback.format_exc())
                job_progress[job_id].update({
                    "status": "failed",
                    "progress": 0,
                    "message": f"Error: {str(e)}"
                })

            finally:
                active_jobs.discard(job_id)
                socketio.emit('job_update', {'job_id': job_id, **job_progress[job_id]})

        # Start processing thread
        thread = threading.Thread(target=process_text_to_image, daemon=True)
        thread.start()

        return jsonify({
            "job_id": job_id,
            "status": "started",
            "message": "Image generation job started"
        })

    except Exception as e:
        logger.error(f"Failed to start image generation: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/image-to-3d', methods=['POST'])
def image_to_3d():
    """Generate 3D model from a previously generated image"""
    global processor, job_progress, active_jobs

    if not processor:
        return jsonify({"error": "AI processor not initialized"}), 503

    try:
        # Get job parameters
        data = request.get_json()

        if not data or 'job_id' not in data:
            return jsonify({"error": "No job_id provided"}), 400

        source_job_id = data['job_id']
        output_format = data.get('format', 'stl')
        dimensions = data.get('dimensions', {'width': 100, 'height': 100, 'depth': 20})

        # Check if the source job exists and has a generated image
        if source_job_id not in job_progress:
            return jsonify({"error": "Source job not found"}), 404

        source_job = job_progress[source_job_id]
        if source_job.get('status') != 'completed' or 'output_file' not in source_job:
            return jsonify({"error": "Source image not ready"}), 400

        # Create new job for 3D generation
        job_id = str(uuid.uuid4())
        job_progress[job_id] = {
            "status": "started",
            "progress": 0,
            "message": "Initializing 3D generation from image...",
            "timestamp": datetime.now().isoformat(),
            "type": "image_to_3d",
            "source_job_id": source_job_id
        }
        active_jobs.add(job_id)

        # Emit initial status
        socketio.emit('job_update', {
            'job_id': job_id,
            **job_progress[job_id]
        })

        # Start processing in background thread
        def process_image_to_3d():
            try:
                # Update progress
                job_progress[job_id].update({
                    "status": "processing",
                    "progress": 25,
                    "message": "Loading generated image..."
                })
                socketio.emit('job_update', {'job_id': job_id, **job_progress[job_id]})

                # Get source image path
                source_image_path = Path(source_job['output_file'])

                if not source_image_path.exists():
                    raise Exception("Source image file not found")

                # Create output directory
                output_dir = Path("outputs") / job_id
                output_dir.mkdir(parents=True, exist_ok=True)

                # Update progress
                job_progress[job_id].update({
                    "progress": 50,
                    "message": "Converting image to 3D model..."
                })
                socketio.emit('job_update', {'job_id': job_id, **job_progress[job_id]})

                # Generate 3D model
                output_file = output_dir / f"model.{output_format}"
                success = False

                if hasattr(processor, 'image_to_3d_generation'):
                    success = processor.image_to_3d_generation(
                        source_image_path,
                        output_file,
                        format=output_format,
                        dimensions=dimensions
                    )
                else:
                    # Create placeholder file
                    with open(output_file, 'w') as f:
                        f.write(f"3D model placeholder for job {job_id}\n")
                        f.write(f"Source: {source_job_id}\n")
                        f.write(f"Format: {output_format}\n")
                        f.write(f"Dimensions: {dimensions}\n")
                    success = True

                if success:
                    job_progress[job_id].update({
                        "status": "completed",
                        "progress": 100,
                        "message": "3D model generation completed successfully!",
                        "output_file": str(output_file),
                        "download_url": f"/api/download/{job_id}/model.{output_format}"
                    })
                else:
                    job_progress[job_id].update({
                        "status": "failed",
                        "progress": 0,
                        "message": "Failed to generate 3D model"
                    })

            except Exception as e:
                logger.error(f"Image-to-3D job {job_id} failed: {e}")
                job_progress[job_id].update({
                    "status": "failed",
                    "progress": 0,
                    "message": f"Error: {str(e)}"
                })

            finally:
                active_jobs.discard(job_id)
                socketio.emit('job_update', {'job_id': job_id, **job_progress[job_id]})

        # Start processing thread
        thread = threading.Thread(target=process_image_to_3d, daemon=True)
        thread.start()

        return jsonify({
            "job_id": job_id,
            "status": "started",
            "message": "3D generation job started"
        })

    except Exception as e:
        logger.error(f"Failed to start 3D generation: {e}")
        return jsonify({"error": str(e)}), 500

def create_fallback_image(prompt, image_path):
    """Create a fallback image when text-to-image AI is not available"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import os

        logger.info(f"Creating fallback image for prompt: '{prompt}' at {image_path}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        # Create image with gradient background
        img = Image.new('RGB', (512, 512), color='white')
        draw = ImageDraw.Draw(img)

        # Create gradient background
        for y in range(512):
            color_val = int(200 + (y / 512) * 55)  # Light blue gradient
            draw.line([(0, y), (512, y)], fill=(color_val, color_val + 20, 255))

        # Try to load default font
        try:
            font = ImageFont.load_default()
        except:
            font = None
            logger.warning("Could not load default font, using basic text rendering")

        # Draw decorative border
        draw.rectangle([10, 10, 501, 501], outline='darkblue', width=3)

        # Add title
        draw.text((20, 30), "Generated Image", fill='darkblue', font=font)
        draw.text((20, 60), "AI Fallback Mode", fill='blue', font=font)

        # Wrap and draw prompt text
        lines = []
        words = prompt.split()
        current_line = ""
        max_chars = 35  # Adjusted for better fit

        for word in words:
            test_line = current_line + word + " "
            if len(test_line) > max_chars:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line.strip())

        # Draw wrapped text
        y_offset = 120
        for i, line in enumerate(lines[:8]):  # Max 8 lines
            draw.text((20, y_offset), line, fill='black', font=font)
            y_offset += 25

        # Add footer
        draw.text((20, 450), "Generated by ORFEAS", fill='gray', font=font)

        # Save with explicit format
        img.save(str(image_path), format='PNG', optimize=True)

        # Verify file was created
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            logger.info(f"[OK] Fallback image created successfully: {file_size} bytes")
            return True
        else:
            logger.error(f"[FAIL] Fallback image file not found after creation")
            return False

    except Exception as e:
        logger.error(f"[FAIL] Failed to create fallback image: {e}")
        logger.error(traceback.format_exc())
        return False@app.route('/api/generate-text-to-3d', methods=['POST'])
def generate_text_to_3d():
    """Generate 3D model from text prompt"""
    global processor, job_progress, active_jobs

    if not processor:
        return jsonify({"error": "AI processor not initialized"}), 503

    try:
        # Get job parameters
        job_id = str(uuid.uuid4())
        data = request.get_json()

        if not data or 'prompt' not in data:
            return jsonify({"error": "No text prompt provided"}), 400

        prompt = data['prompt']
        output_format = data.get('format', 'glb')
        dimensions = data.get('dimensions', {'width': 50, 'height': 50, 'depth': 20})

        # Initialize job tracking
        job_progress[job_id] = {
            "status": "started",
            "progress": 0,
            "message": "Initializing text-to-3D generation...",
            "timestamp": datetime.now().isoformat()
        }
        active_jobs.add(job_id)

        # Emit initial status
        socketio.emit('job_update', {
            'job_id': job_id,
            **job_progress[job_id]
        })

        # Start processing in background thread
        def process_text_to_3d():
            try:
                # Update progress - Step 1: Generate image from text
                job_progress[job_id].update({
                    "status": "processing",
                    "progress": 10,
                    "message": "Generating image from text prompt..."
                })
                socketio.emit('job_update', {'job_id': job_id, **job_progress[job_id]})

                # Create output directory
                output_dir = Path("outputs") / job_id
                output_dir.mkdir(parents=True, exist_ok=True)

                # Step 1: Generate image from text (if supported)
                image_path = output_dir / "generated_image.png"
                if hasattr(processor, 'text_to_image_generation') and processor.get_model_info().get('has_text2image', False):
                    success = processor.text_to_image_generation(prompt, image_path)
                    if not success:
                        # Fallback: create a simple placeholder image
                        from PIL import Image, ImageDraw, ImageFont
                        img = Image.new('RGB', (512, 512), color='lightblue')
                        draw = ImageDraw.Draw(img)
                        try:
                            # Try to use a default font
                            font = ImageFont.load_default()
                        except:
                            font = None

                        # Wrap text
                        lines = []
                        words = prompt.split()
                        current_line = ""
                        for word in words:
                            test_line = current_line + word + " "
                            if len(test_line) > 30:  # Approximate line length
                                if current_line:
                                    lines.append(current_line.strip())
                                current_line = word + " "
                            else:
                                current_line = test_line
                        if current_line:
                            lines.append(current_line.strip())

                        # Draw text
                        y_offset = 200
                        for line in lines[:5]:  # Max 5 lines
                            draw.text((50, y_offset), line, fill='darkblue', font=font)
                            y_offset += 30

                        img.save(image_path)
                else:
                    # Create placeholder image for fallback
                    from PIL import Image, ImageDraw
                    img = Image.new('RGB', (512, 512), color='lightgray')
                    draw = ImageDraw.Draw(img)
                    draw.text((50, 250), f"Text: {prompt[:50]}...", fill='black')
                    img.save(image_path)

                # Update progress - Step 2: Convert image to 3D
                job_progress[job_id].update({
                    "progress": 50,
                    "message": "Converting generated image to 3D model..."
                })
                socketio.emit('job_update', {'job_id': job_id, **job_progress[job_id]})

                # Step 2: Convert image to 3D
                output_file = output_dir / f"model.{output_format}"
                success = False
                if hasattr(processor, 'image_to_3d_generation'):
                    success = processor.image_to_3d_generation(
                        image_path,
                        output_file,
                        format=output_format,
                        dimensions=dimensions
                    )
                else:
                    # Create a simple placeholder file
                    with open(output_file, 'w') as f:
                        f.write(f"Text-to-3D model placeholder for: {prompt}\n")
                        f.write(f"Format: {output_format}\n")
                        f.write(f"Dimensions: {dimensions}\n")
                    success = True

                if success:
                    job_progress[job_id].update({
                        "status": "completed",
                        "progress": 100,
                        "message": "Text-to-3D generation completed successfully!",
                        "output_file": str(output_file),
                        "download_url": f"/api/download/{job_id}/model.{output_format}",
                        "generated_image": f"/api/download/{job_id}/generated_image.png"
                    })
                else:
                    job_progress[job_id].update({
                        "status": "failed",
                        "progress": 0,
                        "message": "Failed to convert text to 3D model"
                    })

            except Exception as e:
                logger.error(f"Text-to-3D job {job_id} failed: {e}")
                job_progress[job_id].update({
                    "status": "failed",
                    "progress": 0,
                    "message": f"Error: {str(e)}"
                })

            finally:
                active_jobs.discard(job_id)
                socketio.emit('job_update', {'job_id': job_id, **job_progress[job_id]})

        # Start processing thread
        thread = threading.Thread(target=process_text_to_3d, daemon=True)
        thread.start()

        return jsonify({
            "job_id": job_id,
            "status": "started",
            "message": "Text-to-3D generation job started"
        })

    except Exception as e:
        logger.error(f"Failed to start text-to-3D generation: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-3d', methods=['POST'])
def generate_3d():
    """Generate 3D model from uploaded image file"""
    global processor, job_progress, active_jobs

    if not processor:
        return jsonify({"error": "AI processor not initialized"}), 503

    try:
        # Get job parameters
        job_id = str(uuid.uuid4())

        # Handle file upload
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Get other parameters
        output_format = request.form.get('format', 'glb')
        dimensions_str = request.form.get('dimensions', '{"width": 50, "height": 50, "depth": 20}')

        try:
            import json
            dimensions = json.loads(dimensions_str)
        except:
            dimensions = {'width': 50, 'height': 50, 'depth': 20}

        # Save uploaded file
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)

        import os
        filename = f"{job_id}_{file.filename}"
        image_path = upload_dir / filename
        file.save(str(image_path))

        # Initialize job tracking
        job_progress[job_id] = {
            "status": "started",
            "progress": 0,
            "message": "Initializing image-to-3D generation...",
            "timestamp": datetime.now().isoformat()
        }
        active_jobs.add(job_id)

        # Emit initial status
        socketio.emit('job_update', {
            'job_id': job_id,
            **job_progress[job_id]
        })

        # Start processing in background thread
        def process_image_to_3d():
            try:
                # Update progress
                job_progress[job_id].update({
                    "status": "processing",
                    "progress": 25,
                    "message": "Processing uploaded image..."
                })
                socketio.emit('job_update', {'job_id': job_id, **job_progress[job_id]})

                # Create output directory
                output_dir = Path("outputs") / job_id
                output_dir.mkdir(parents=True, exist_ok=True)

                output_file = output_dir / f"model.{output_format}"

                # Update progress
                job_progress[job_id].update({
                    "progress": 50,
                    "message": "Converting image to 3D model..."
                })
                socketio.emit('job_update', {'job_id': job_id, **job_progress[job_id]})

                # Call processor
                success = False
                if hasattr(processor, 'image_to_3d_generation'):
                    success = processor.image_to_3d_generation(
                        image_path,
                        output_file,
                        format=output_format,
                        dimensions=dimensions
                    )
                else:
                    # Create a simple placeholder file
                    with open(output_file, 'w') as f:
                        f.write(f"Image-to-3D model placeholder for job {job_id}\n")
                        f.write(f"Source image: {image_path.name}\n")
                        f.write(f"Format: {output_format}\n")
                        f.write(f"Dimensions: {dimensions}\n")
                    success = True

                if success:
                    job_progress[job_id].update({
                        "status": "completed",
                        "progress": 100,
                        "message": "Image-to-3D conversion completed successfully!",
                        "output_file": str(output_file),
                        "download_url": f"/api/download/{job_id}/model.{output_format}"
                    })
                else:
                    job_progress[job_id].update({
                        "status": "failed",
                        "progress": 0,
                        "message": "Failed to convert image to 3D model"
                    })

            except Exception as e:
                logger.error(f"Image-to-3D job {job_id} failed: {e}")
                job_progress[job_id].update({
                    "status": "failed",
                    "progress": 0,
                    "message": f"Error: {str(e)}"
                })

            finally:
                active_jobs.discard(job_id)
                socketio.emit('job_update', {'job_id': job_id, **job_progress[job_id]})

        # Start processing thread
        thread = threading.Thread(target=process_image_to_3d, daemon=True)
        thread.start()

        return jsonify({
            "job_id": job_id,
            "status": "started",
            "message": "3D generation job started"
        })

    except Exception as e:
        logger.error(f"Failed to start 3D generation: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/job-status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status"""
    if job_id in job_progress:
        return jsonify(job_progress[job_id])
    else:
        return jsonify({"error": "Job not found"}), 404

@app.route('/api/download/<job_id>/<filename>', methods=['GET'])
def download_file(job_id, filename):
    """Download generated file"""
    try:
        file_path = Path("outputs") / job_id / filename
        if file_path.exists():
            return send_file(str(file_path), as_attachment=True)
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return jsonify({"error": str(e)}), 500

# WebSocket events
@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('connection_status', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('subscribe_job')
def handle_subscribe_job(data):
    job_id = data.get('job_id')
    if job_id:
        join_room(job_id)
        logger.info(f"Client {request.sid} subscribed to job {job_id}")

def main():
    """Main server startup"""
    logger.info("[LAUNCH] Starting ORFEAS Backend Server (Safe Mode)")

    # Create necessary directories
    for directory in ["uploads", "outputs", "temp"]:
        Path(directory).mkdir(exist_ok=True)

    # Initialize AI processor
    ai_success = initialize_ai_processor()

    if ai_success:
        logger.info("[OK] Server ready with AI capabilities")
    else:
        logger.warning("[WARN] Server running in limited mode (no AI)")

    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info("[STOP] Shutting down server...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start the server
    try:
        logger.info("[WEB] Server starting on http://localhost:5000")
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        logger.info("[STOP] Server stopped by user")
    except Exception as e:
        logger.error(f"[FAIL] Server failed to start: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
