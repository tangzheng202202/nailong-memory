#!/usr/bin/env python3
"""
Webhook 接收端点测试服务器
用于测试 OpenClaw 的 webhook 接收功能
"""

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from pathlib import Path

# 配置
PORT = 8080
LOG_FILE = Path.home() / ".openclaw" / "logs" / "webhook-server.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

class WebhookHandler(BaseHTTPRequestHandler):
    """处理 webhook 请求"""
    
    def log_message(self, format, *args):
        """自定义日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {format % args}\n"
        
        # 写入文件
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
        
        # 输出到控制台
        print(log_entry.strip())
    
    def _send_response(self, status_code=200, message="OK"):
        """发送响应"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = json.dumps({"status": message, "timestamp": datetime.now().isoformat()})
        self.wfile.write(response.encode())
    
    def do_GET(self):
        """处理 GET 请求 - 健康检查"""
        self.log_message("GET %s - Health check", self.path)
        self._send_response(200, "Webhook server is running")
    
    def do_POST(self):
        """处理 POST 请求 - 接收 webhook"""
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        
        # 记录请求信息
        self.log_message("POST %s - Webhook received", self.path)
        self.log_message("Headers: %s", dict(self.headers))
        
        # 尝试解析 JSON
        try:
            if post_data:
                payload = json.loads(post_data.decode())
                self.log_message("Payload: %s", json.dumps(payload, indent=2))
            else:
                payload = {}
                self.log_message("Payload: (empty)")
            
            # 保存 webhook 到文件
            webhook_file = LOG_FILE.parent / f"webhook-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            with open(webhook_file, "w") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "path": self.path,
                    "headers": dict(self.headers),
                    "payload": payload
                }, f, indent=2)
            
            self.log_message("Saved to: %s", webhook_file)
            self._send_response(200, "Webhook received")
            
        except json.JSONDecodeError as e:
            self.log_message("Error parsing JSON: %s", str(e))
            self._send_response(400, "Invalid JSON")
        except Exception as e:
            self.log_message("Error: %s", str(e))
            self._send_response(500, str(e))

def run_server(port=PORT):
    """启动 webhook 服务器"""
    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    print(f"🚀 Webhook 服务器启动")
    print(f"📡 监听地址: http://0.0.0.0:{port}")
    print(f"📝 日志文件: {LOG_FILE}")
    print(f"\n测试命令:")
    print(f"  健康检查: curl http://localhost:{port}/")
    print(f"  发送 webhook: curl -X POST http://localhost:{port}/webhook -H 'Content-Type: application/json' -d '{{\"test\": \"data\"}}'")
    print(f"\n按 Ctrl+C 停止服务器\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
        server.shutdown()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(port)
