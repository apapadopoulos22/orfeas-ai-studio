#!/usr/bin/env python
"""
ORFEAS Backend Process Manager
Keeps the backend running on Windows with automatic restart
"""
import subprocess
import sys
import time
import os

def run_backend():
    """Run backend with auto-restart on crash"""
    restart_count = 0
    max_restarts = 10

    print("=" * 80)
    print("ORFEAS Backend Manager - Starting")
    print("=" * 80)
    print(f"Log file: backend/logs/backend_requests.log")
    print(f"Port: 5000")
    print("=" * 80)

    os.chdir("backend")

    while restart_count < max_restarts:
        print(f"\n[MANAGER] Starting backend (attempt {restart_count + 1}/{max_restarts})")
        print(f"[MANAGER] Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # Start backend process
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True
            )

            # Wait for process to exit
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                print(line, end='')

            returncode = process.wait()
            print(f"\n[MANAGER] Backend exited with code {returncode}")

            restart_count += 1
            if restart_count < max_restarts:
                wait_time = min(5 * restart_count, 30)  # Exponential backoff, max 30 seconds
                print(f"[MANAGER] Restarting in {wait_time} seconds...")
                time.sleep(wait_time)

        except KeyboardInterrupt:
            print("\n[MANAGER] Received interrupt, shutting down")
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
            sys.exit(0)
        except Exception as e:
            print(f"\n[MANAGER] Error: {e}")
            restart_count += 1
            if restart_count < max_restarts:
                time.sleep(5)

    print(f"\n[MANAGER] Max restart attempts ({max_restarts}) reached. Exiting.")
    sys.exit(1)

if __name__ == "__main__":
    run_backend()
