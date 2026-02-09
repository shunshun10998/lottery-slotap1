from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo=1155"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.dhlottery.co.kr/",
        })

        try:
            with urllib.request.urlopen(req, timeout=10) as res:
                raw = res.read().decode()
                data = json.loads(raw)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "raw_response": data,
            }, ensure_ascii=False).encode())

        except Exception as e:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "error_type": type(e).__name__,
                "error_msg": str(e),
            }).encode())