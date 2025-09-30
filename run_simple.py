#!/usr/bin/env python3
"""Simple development server launcher using Python's built-in HTTP server"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Simple test server
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime
from urllib.parse import urlparse

class SimpleAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "2.0.0",
                "service": "trading-signal-alerts"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif parsed_path.path == '/' or parsed_path.path == '':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "app": "Trading Signal Alerts",
                "version": "2.0.0",
                "description": "Trading signal alerting system",
                "health": "/health"
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {"error": "Not found", "path": parsed_path.path}
            self.wfile.write(json.dumps(response).encode())

if __name__ == "__main__":
    print("🚀 Starting Simple Trading Signal Backend...")
    print("💡 Health check: http://localhost:8001/health")
    print("🏠 Root: http://localhost:8001/")
    print("")
    
    server = HTTPServer(('localhost', 8001), SimpleAPIHandler)
    print("✅ Server running on http://localhost:8001")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        server.shutdown()