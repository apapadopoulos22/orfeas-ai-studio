================================================================================
ORFEAS Local Dev Server - Advanced Version with Auto-Reload
================================================================================

This script:
1. Starts HTTP server on port 8000
2. Monitors HTML files for changes
3. Displays console messages with dev info
4. Shows connection status

Setup:
    cd c:\Users\johng\Documents\oscar
    .\START_LOCAL_DEV_SERVER.ps1

Then open:
    http://localhost:8000/orfeas-ai-studio.html

================================================================================

import os
import sys
import http.server
import socketserver
import threading
import time
from pathlib import Path
from datetime import datetime

# ============================================================================
# Configuration
# ============================================================================

PORT = 8000
WORKSPACE = r"c:\Users\johng\Documents\oscar"
HTML_FILES = [
    "orfeas-ai-studio.html",
    "synexa-style-studio.html",
    "batch-studio.html",
    "bob-ai-chat.html",
    "orfeas-studio-responsive.html",
    "orfeas-studio.html"
]

# File modification times for change detection
file_mtimes = {}

# ============================================================================
# Custom HTTP Handler with Logging
# ============================================================================

class DevServerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORKSPACE, **kwargs)

    def do_GET(self):
        """Handle GET requests with logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        method_color = "\033[92m"  # Green

        # Log request
        print(f"[{timestamp}] {method_color}GET{'\033[0m'} {self.path}")

        # Serve file
        super().do_GET()

    def log_message(self, format, *args):
        """Override to reduce verbose logging"""
        pass  # Suppress default logging

# ============================================================================
# File Watcher
# ============================================================================

def watch_files():
    """Monitor HTML files for changes"""
    global file_mtimes

    print("\n📁 Monitoring HTML files for changes...")
    print("-" * 60)

    while True:
        time.sleep(2)

        for html_file in HTML_FILES:
            path = os.path.join(WORKSPACE, html_file)

            if not os.path.exists(path):
                continue

            current_mtime = os.path.getmtime(path)

            if html_file not in file_mtimes:
                file_mtimes[html_file] = current_mtime
            elif file_mtimes[html_file] != current_mtime:
                timestamp = datetime.now().strftime("%H:%M:%S")
                file_mtimes[html_file] = current_mtime
                print(f"\n✏️  [{timestamp}] CHANGED: {html_file}")
                print(f"   💡 Hint: Refresh browser to see changes (Ctrl+R or F5)")
                print("-" * 60 + "\n")

# ============================================================================
# Main Server
# ============================================================================

def main():
    os.chdir(WORKSPACE)

    print("\n" + "=" * 60)
    print("🚀 ORFEAS LOCAL DEVELOPMENT SERVER")
    print("=" * 60 + "\n")

    # Print startup info
    print("📍 Configuration:")
    print(f"   Directory: {WORKSPACE}")
    print(f"   Port:      {PORT}")
    print(f"   URL:       http://localhost:{PORT}")
    print("\n📄 HTML Files Being Served:")
    for html_file in HTML_FILES:
        path = os.path.join(WORKSPACE, html_file)
        status = "✅" if os.path.exists(path) else "❌"
        print(f"   {status} http://localhost:{PORT}/{html_file}")

    print("\n🔗 Backend URLs:")
    print(f"   Local:  http://127.0.0.1:5000")
    print(f"   ngrok:  https://unsaid-ellsworth-uncorrespondingly.ngrok-free.dev")

    print("\n" + "=" * 60)

    # Start file watcher in background thread
    watcher_thread = threading.Thread(target=watch_files, daemon=True)
    watcher_thread.start()

    # Start HTTP server
    try:
        with socketserver.TCPServer(("", PORT), DevServerHandler) as httpd:
            print(f"\n✅ Server started on http://localhost:{PORT}")
            print("\n💡 Tips:")
            print("   • Edit HTML files and refresh browser to see changes instantly")
            print("   • Check browser F12 Console for backend connection status")
            print("   • File changes are monitored (watch terminal for updates)")
            print("\n🛑 Press Ctrl+C to stop server\n")

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n\n🛑 Shutting down server...")
                sys.exit(0)

    except OSError as e:
        if e.errno == 48:  # Port already in use
            print(f"\n❌ ERROR: Port {PORT} is already in use!")
            print("   Either:")
            print(f"   1. Kill the process using port {PORT}")
            print(f"   2. Change PORT variable in this script")
        else:
            print(f"\n❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
