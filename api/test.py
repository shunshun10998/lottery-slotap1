from http.server import BaseHTTPRequestHandler
import urllib.request
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 대안 API 테스트
        apis = {
            "api1": "https://api.nlotto.co.kr/common.do?method=getLottoNumber&drwNo=1155",
            "api2": "https://www.nlotto.co.kr/common.do?method=getLottoNumber&drwNo=1155",
        }

        results = {}
        for name, url in apis.items():
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0",
                })
                with urllib.request.urlopen(req, timeout=10) as res:
                    raw = res.read().decode("utf-8", errors="replace")
                    # JSON인지 확인
                    if raw.strip().startswith("{"):
                        results[name] = {"status": "JSON", "data": json.loads(raw)}
                    else:
                        results[name] = {"status": "HTML", "preview": raw[:200]}
            except Exception as e:
                results[name] = {"status": "error", "msg": str(e)}

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(results, ensure_ascii=False).encode())