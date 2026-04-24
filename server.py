# -*- coding: utf-8 -*-
"""卖水统计表 - 本地云服务器"""
import http.server
import json
import os
import threading
import time
from datetime import datetime

PORT = 8080
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'water_data.json')
HTML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')

_lock = threading.Lock()

def load_data():
    """加载所有数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    """保存所有数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 全局版本号，用于变更通知
_version = int(time.time() * 1000)

class WaterHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # 简化日志
        pass

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        global _version
        if self.path == '/' or self.path == '/index.html':
            # 提供HTML页面
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self._cors()
            self.end_headers()
            if os.path.exists(HTML_FILE):
                with open(HTML_FILE, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write('页面文件不存在'.encode('utf-8'))
        elif self.path == '/api/data':
            # 返回所有数据
            with _lock:
                data = load_data()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({'data': data, 'version': _version}, ensure_ascii=False).encode('utf-8'))
        elif self.path.startswith('/api/data/'):
            # 返回单个key
            key = self.path[len('/api/data/'):]
            with _lock:
                data = load_data()
            item = data.get(key, None)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._cors()
            self.end_headers()
            if item:
                self.wfile.write(json.dumps({'value': item.get('value'), 'updated_at': item.get('updated_at'), 'version': _version}, ensure_ascii=False).encode('utf-8'))
            else:
                self.wfile.write(b'{"value":null,"version":0}')
        elif self.path == '/api/version':
            # 版本检查（轻量级轮询）
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({'version': _version}).encode('utf-8'))
        elif self.path == '/api/ping':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._cors()
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        else:
            self.send_error(404)

    def do_POST(self):
        global _version
        if self.path == '/api/data':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                item = json.loads(post_data.decode('utf-8'))
            except:
                self.send_error(400, 'Invalid JSON')
                return

            key = item.get('key')
            value = item.get('value')
            if not key:
                self.send_error(400, 'Missing key')
                return

            with _lock:
                data = load_data()
                data[key] = {
                    'value': value,
                    'updated_at': datetime.now().isoformat()
                }
                save_data(data)
                _version = int(time.time() * 1000)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'version': _version}).encode('utf-8'))
        else:
            self.send_error(404)

def run_server():
    server = http.server.HTTPServer(('0.0.0.0', PORT), WaterHandler)
    print(f'========================================')
    print(f'  卖水统计表服务器已启动！')
    print(f'========================================')
    print(f'  本地访问: http://localhost:{PORT}')
    print(f'  局域网:   http://192.168.3.90:{PORT}')
    print(f'  公网:     http://175.4.22.6:{PORT}')
    print(f'========================================')
    print(f'  数据文件: {DATA_FILE}')
    print(f'  页面文件: {HTML_FILE}')
    print(f'========================================')
    print(f'  按 Ctrl+C 停止服务器')
    print(f'========================================')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n服务器已停止')
        server.shutdown()

if __name__ == '__main__':
    run_server()
