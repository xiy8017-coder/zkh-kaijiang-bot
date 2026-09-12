import os
import json
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

API_KEY = os.environ.get("YU28_API_KEY", "")
PORT = int(os.environ.get("PORT", "8080"))

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/kj.json"):
            self.proxy_kj()
        else:
            super().do_GET()

    def proxy_kj(self):
        if not API_KEY:
            self.send_json({"error": "YU28_API_KEY 未配置"}, 500)
            return
        req = urllib.request.Request(
            "https://yu28.top" + self.path,
            headers={"X-Api-Key": API_KEY, "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                data = r.read()
                self.send_response(r.status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            self.send_json({"error": "YU28 API 请求失败", "status": e.code}, e.code)
        except Exception as e:
            self.send_json({"error": "服务器连接开奖数据失败", "detail": str(e)}, 502)

    def send_json(self, obj, status=200):
        data=json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    print(f"小濠国际杀组网站启动，端口 {PORT}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
