#!/usr/bin/env python3
"""
Start Django development server and open in browser
Usage: python run_server.py
"""
import subprocess
import webbrowser
import time
import sys
import socket
from threading import Thread

def wait_for_server(host='127.0.0.1', port=8000, timeout=30):
    """Wait for the server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
            time.sleep(0.5)
        except:
            time.sleep(0.5)
    return False

def open_browser_when_ready():
    """Wait for server to be ready, then open browser"""
    print("⏳ Waiting for server to start...")
    if wait_for_server():
        print("✅ Server is ready!")
        print("🌐 Opening browser...")
        time.sleep(0.5)  # Small extra delay for safety
        webbrowser.open('http://127.0.0.1:8000')
    else:
        print("⚠️  Server took too long to start. Please open browser manually.")

def run_server():
    """Start Django development server and open browser"""
    try:
        print("🚀 Starting R1D3 Django server...")
        print("📍 Server will be available at: http://127.0.0.1:8000")
        
        # Start browser opener in background thread
        browser_thread = Thread(target=open_browser_when_ready, daemon=True)
        browser_thread.start()
        
        # Start Django server (this blocks)
        subprocess.run(['python', 'manage.py', 'runserver'], check=True)
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        print("\n💡 Tip: Make sure you're in the project directory and have run migrations")
        sys.exit(1)

if __name__ == "__main__":
    run_server()
