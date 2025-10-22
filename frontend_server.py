"""
ORFEAS Frontend Server with Auto-Start Backend Capability

This server serves the orfeas-studio.html frontend and provides an API
endpoint that can start the backend server automatically, bypassing
browser security restrictions.

Usage:
    python frontend_server.py

Then open: http://localhost:8000
"""

import os
import sys
import subprocess
import socket
import time
import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
from typing import Any, Dict, List

# Configuration
FRONTEND_PORT = 8000
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 5000  # Fixed: Backend actually runs on port 5000, not 5002
BACKEND_HEALTH_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api/health"
SCRIPT_DIR = Path(__file__).parent.absolute()

# Global backend process reference
backend_process = None
backend_starting = False

class ORFEASFrontendHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler with backend auto-start capability"""

    def __init__(self, *args, **kwargs) -> None:
        # Set the directory to serve files from
        super().__init__(*args, directory=str(SCRIPT_DIR), **kwargs)

    def log_message(self, format: Any, *args) -> None:
        """Custom log format"""
        print(f"[FRONTEND] {self.address_string()} - {format % args}")

    def do_GET(self) -> None:
        """Handle GET requests"""
        parsed_path = urlparse(self.path)

        # API: Check backend status
        if parsed_path.path == '/api/frontend/backend-status':
            self.handle_backend_status()
            return

        # API: Start backend
        elif parsed_path.path == '/api/frontend/start-backend':
            self.handle_start_backend()
            return

        # Serve index.html for root path
        elif parsed_path.path == '/':
            self.path = '/orfeas-studio.html'

        # Serve static files
        super().do_GET()

    def handle_backend_status(self) -> None:
        """Check if backend is running"""
        try:
            import urllib.request
            with urllib.request.urlopen(BACKEND_HEALTH_URL, timeout=2) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    self.send_json_response({
                        "running": True,
                        "starting": False,
                        "backend_data": data
                    })
                    return
        except Exception as e:
            pass

        # Backend not running
        global backend_starting
        self.send_json_response({
            "running": False,
            "starting": backend_starting
        })

    def handle_start_backend(self) -> None:
        """Start the backend server automatically"""
        global backend_process, backend_starting

        if backend_starting:
            self.send_json_response({
                "success": False,
                "message": "Backend is already starting",
                "starting": True
            })
            return

        # Check if backend is already running
        try:
            import urllib.request
            with urllib.request.urlopen(BACKEND_HEALTH_URL, timeout=2) as response:
                if response.status == 200:
                    self.send_json_response({
                        "success": True,
                        "message": "Backend is already running",
                        "running": True
                    })
                    return
        except Exception:
            pass

        # Start backend in separate thread
        backend_starting = True
        thread = threading.Thread(target=self.start_backend_async)
        thread.daemon = True
        thread.start()

        self.send_json_response({
            "success": True,
            "message": "Backend startup initiated",
            "starting": True
        })

    def start_backend_async(self) -> None:
        """Start backend server asynchronously"""
        global backend_process, backend_starting

        try:
            print("\n" + "="*70)
            print("[LAUNCH] STARTING BACKEND SERVER AUTOMATICALLY")
            print("="*70)

            # Determine the backend directory
            backend_dir = SCRIPT_DIR / "backend"

            if not backend_dir.exists():
                print(f"[FAIL] Backend directory not found: {backend_dir}")
                backend_starting = False
                return

            # Find main.py
            main_py = backend_dir / "main.py"
            if not main_py.exists():
                print(f"[FAIL] Backend main.py not found: {main_py}")
                backend_starting = False
                return

            print(f"[OK] Found backend: {main_py}")
            print(f"üìÇ Working directory: {backend_dir}")

            # Determine Python executable
            python_exe = sys.executable
            print(f"Ô£ø√º√™√ß Using Python: {python_exe}")

            # Start backend process
            if os.name == 'nt':  # Windows
                # Use CREATE_NEW_CONSOLE to open in new window
                CREATE_NEW_CONSOLE = 0x00000010
                backend_process = subprocess.Popen(
                    [python_exe, "main.py"],
                    cwd=str(backend_dir),
                    creationflags=CREATE_NEW_CONSOLE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:  # Linux/Mac
                backend_process = subprocess.Popen(
                    [python_exe, "main.py"],
                    cwd=str(backend_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

            print(f"[OK] Backend process started (PID: {backend_process.pid})")
            print(f"[WAIT] Waiting for backend to initialize...")

            # Wait for backend to be ready (max 45 seconds to allow model loading)
            max_attempts = 45
            for attempt in range(1, max_attempts + 1):
                time.sleep(1)
                try:
                    import urllib.request
                    with urllib.request.urlopen(BACKEND_HEALTH_URL, timeout=2) as response:
                        if response.status == 200:
                            print(f"[OK] Backend is now running on http://{BACKEND_HOST}:{BACKEND_PORT}")
                            print("="*70)
                            backend_starting = False
                            return
                except Exception:
                    print(f"[WAIT] Waiting for backend... ({attempt}/{max_attempts})")

            print(f"[WARN] Backend started but health check failed after {max_attempts} seconds")
            print("   Check the backend window for errors")
            print("="*70)

        except Exception as e:
            print(f"[FAIL] Failed to start backend: {e}")
            import traceback
            traceback.print_exc()
        finally:
            backend_starting = False

    def send_json_response(self, data: Dict, status: List = 200) -> None:
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def end_headers(self) -> None:
        """Add CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()


def check_port_available(port: Any) -> int:
    """Check if port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('', port))
        sock.close()
        return True
    except OSError:
        return False


def main() -> None:
    """Start the frontend server"""
    print("\n" + "="*70)
    print("[WEB] ORFEAS FRONTEND SERVER")
    print("   With Automatic Backend Startup")
    print("="*70)

    # Check if port is available
    if not check_port_available(FRONTEND_PORT):
        print(f"\n[FAIL] ERROR: Port {FRONTEND_PORT} is already in use")
        print(f"   Please close any application using port {FRONTEND_PORT}")
        print(f"   Or run: netstat -ano | findstr :{FRONTEND_PORT}")
        print("="*70)
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Check if orfeas-studio.html exists
    html_file = SCRIPT_DIR / "orfeas-studio.html"
    if not html_file.exists():
        print(f"\n[FAIL] ERROR: orfeas-studio.html not found")
        print(f"   Expected: {html_file}")
        print("="*70)
        input("\nPress Enter to exit...")
        sys.exit(1)

    print(f"\n[OK] Frontend file: {html_file.name}")
    print(f"[OK] Server port: {FRONTEND_PORT}")
    print(f"[OK] Backend target: http://{BACKEND_HOST}:{BACKEND_PORT}")
    print(f"\nüìÇ Serving from: {SCRIPT_DIR}")
    print("\n" + "="*70)
    print("[LAUNCH] SERVER STARTING...")
    print("="*70)

    # Create HTTP server
    server = HTTPServer(('', FRONTEND_PORT), ORFEASFrontendHandler)

    print(f"\n[OK] Server running on: http://localhost:{FRONTEND_PORT}")
    print(f"[OK] Direct link: http://localhost:{FRONTEND_PORT}/orfeas-studio.html")
    print(f"\n[EDIT] Features:")
    print(f"   ‚Ä¢ Serves orfeas-studio.html frontend")
    print(f"   ‚Ä¢ Automatic backend detection")
    print(f"   ‚Ä¢ Automatic backend startup via API")
    print(f"   ‚Ä¢ No browser security restrictions!")
    print(f"\n[TARGET] OPEN IN BROWSER: http://localhost:{FRONTEND_PORT}")
    print("\n" + "="*70)
    print("‚è∏Ô∏è  Press Ctrl+C to stop the server")
    print("="*70 + "\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("[STOP] Shutting down frontend server...")

        # Stop backend if running
        global backend_process
        if backend_process and backend_process.poll() is None:
            print("[STOP] Stopping backend server...")
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()

        server.shutdown()
        print("[OK] Server stopped")
        print("="*70 + "\n")


if __name__ == "__main__":
    main()
