#!/usr/bin/env python3
"""Development server launcher for Trading Signal Alerts"""

import uvicorn
import os
import sys

if __name__ == "__main__":
    # Add src to Python path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    sys.path.insert(0, src_path)
    
    print("🚀 Starting Trading Signal Alerts Backend...")
    print("📊 API Documentation will be available at: http://localhost:8002/docs")
    print("💡 Health check: http://localhost:8002/health")
    print("")
    
    # Start the server with stable configuration
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8002,  # Use port 8002 to avoid conflicts
        reload=False,  # Disable reload to prevent crashes
        log_level="info",
        access_log=True,
        workers=1,  # Single worker for development
        loop="asyncio"  # Specify event loop
    )
