from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 최근 N회차 데이터 가져오기
            count = 50  # 최근 50회차

            # 최신 회차 찾기
            latest = self._find_latest_round()
            if latest == 0:
                self._send_error("최신 회차를 찾을 수 없습니다")
                return

            # 데이터 수집
            history = []
            for i in range(count):
                round_num = latest - i
                data = self._fetch_round(round_num)
                if data:
                    history.append(data)

            # 통계 계산
            frequency = {}
            for draw in history:
                for num in draw["numbers"]:
                    frequency[num] = frequency.get(num, 0) + 1

            # 응답
            result = {
                "latest_round": latest,
                "total_draws": len(history),
                "history": history[:10],  # 최근 10회만 전송
                "frequency": dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True)),
                "hot_numbers": sorted(frequency, key=frequency.get, reverse=True)[:20],
            }

            self._send_json(result)

        except Exception as e:
            self._send_error(str(e))

    def _find_latest_round(self):
        # 대략적인 최신 회차 추정 후 탐색
        # 2002년 12월 첫 회차, 매주 1회
        import datetime
        weeks = (datetime.date.today() - datetime.date(2002, 12, 7)).days // 7
        guess = weeks + 1

        for offset in range(5):
            for r in [guess - offset, guess + offset]:
                data = self._fetch_round(r)
                if data:
                    return r
        return 0

    def _fetch_round(self, round_num):
        url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={round_num}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.dhlottery.co.kr/",
        })

        try:
            with urllib.request.urlopen(req, timeout=5) as res:
                data = json.loads(res.read().decode())

            if data.get("returnValue") == "success":
                numbers = sorted([
                    data["drwtNo1"], data["drwtNo2"], data["drwtNo3"],
                    data["drwtNo4"], data["drwtNo5"], data["drwtNo6"],
                ])
                return {
                    "round": round_num,
                    "numbers": numbers,
                    "bonus": data["bnusNo"],
                }
        except:
            pass
        return None

    def _send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _send_error(self, msg):
        self.send_response(500)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": msg}).encode())