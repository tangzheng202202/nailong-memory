#!/usr/bin/env python3
"""
Webhook 测试脚本 - 快速测试
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "message": "Webhook server running"}).encode())
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        print(f"\n📨 Webhook received:")
        print(f"   Path: {self.path}")
        print(f"   Data: {post_data.decode()}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "received"}).encode())
    
    def log_message(self, format, *args):
        pass  # 静默日志

if __name__ == "__main__":
    PORT = 8083
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"🚀 Webhook server running at http://127.0.0.1:{PORT}/")
    print("Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        server.shutdown()
