#!/usr/bin/env python3
"""Simple startup script that bypasses database issues."""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    print("🚀 Starting VANTAGE AI Application...")
    
    # Set environment variables
    os.environ["DATABASE_URL"] = "sqlite:///./vantage_ai.db"
    os.environ["SECRET_KEY"] = "VQ8guiKk3G-5yiz0wuBkK8Mv_bTA14Md6kZbVshUwgc="
    os.environ["REDIS_URL"] = "redis://localhost:6379"
    
    # Start the API server
    print("📡 Starting API server on port 8000...")
    api_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app.main:app", 
        "--host", "0.0.0.0", "--port", "8000", "--reload"
    ])
    
    # Wait a moment for API to start
    time.sleep(3)
    
    # Start the web server
    print("🌐 Starting web server on port 3000...")
    web_dir = Path(__file__).parent / "web"
    web_process = subprocess.Popen([
        "npm", "run", "dev"
    ], cwd=web_dir)
    
    print("✅ Application started successfully!")
    print("🔗 API: http://localhost:8000")
    print("🔗 Web: http://localhost:3000")
    print("📚 Docs: http://localhost:8000/docs")
    
    try:
        # Keep running until interrupted
        api_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        api_process.terminate()
        web_process.terminate()
        print("✅ Shutdown complete!")

if __name__ == "__main__":
    main()
