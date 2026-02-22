"""
BMI計算機 - 標準ライブラリのみで動作するシンプルなWebアプリ
Render / ローカル どちらでも動作します
"""
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# ── 定数 ──────────────────────────────────────────────
PORT = int(os.environ.get("PORT", 8000))
HOST = "0.0.0.0"

# ── BMI評価ロジック ────────────────────────────────────
def calc_bmi(height_cm: float, weight_kg: float):  # 戻り値: (bmi: float, label: str)
    """BMI値と評価文字列を返す"""
    if height_cm <= 0 or weight_kg <= 0:
        return 0.0, "入力値が不正です"
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    if bmi < 18.5:
        label = "低体重（痩せ型）"
    elif bmi < 25.0:
        label = "普通体重（標準）"
    elif bmi < 30.0:
        label = "肥満（1度）"
    elif bmi < 35.0:
        label = "肥満（2度）"
    elif bmi < 40.0:
        label = "肥満（3度）"
    else:
        label = "肥満（4度）"
    return round(bmi, 2), label

# ── HTML テンプレート ─────────────────────────────────
def build_html(bmi: float | None = None, label: str = "", error: str = "") -> str:
    result_block = ""
    if error:
        result_block = f'<p class="error">⚠ {error}</p>'
    elif bmi is not None:
        result_block = f"""
        <div class="result">
          <p>BMI値: <strong>{bmi}</strong></p>
          <p>判定: <strong>{label}</strong></p>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BMI計算機</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Helvetica Neue', Arial, sans-serif;
      background: #f0f4f8;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 1rem;
    }}
    .card {{
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,.1);
      padding: 2rem;
      width: 100%;
      max-width: 420px;
    }}
    h1 {{ font-size: 1.5rem; color: #2d3748; margin-bottom: 1.5rem; text-align: center; }}
    label {{ display: block; font-size: .85rem; color: #4a5568; margin-bottom: .25rem; margin-top: 1rem; }}
    input[type=number] {{
      width: 100%; padding: .6rem .8rem;
      border: 1px solid #cbd5e0; border-radius: 8px;
      font-size: 1rem; outline: none;
      transition: border-color .2s;
    }}
    input[type=number]:focus {{ border-color: #4299e1; }}
    .buttons {{ display: flex; gap: .75rem; margin-top: 1.5rem; }}
    button {{
      flex: 1; padding: .7rem;
      border: none; border-radius: 8px;
      font-size: 1rem; cursor: pointer;
      transition: opacity .2s;
    }}
    button:hover {{ opacity: .85; }}
    .btn-calc {{ background: #4299e1; color: #fff; }}
    .btn-clear {{ background: #e2e8f0; color: #4a5568; }}
    .result {{
      margin-top: 1.5rem; padding: 1rem;
      background: #ebf8ff; border-radius: 8px;
      text-align: center; line-height: 1.8;
      color: #2b6cb0;
    }}
    .result strong {{ font-size: 1.2rem; }}
    .error {{
      margin-top: 1.5rem; padding: 1rem;
      background: #fff5f5; border-radius: 8px;
      color: #c53030; text-align: center;
    }}
    .note {{ font-size: .75rem; color: #a0aec0; margin-top: 1rem; text-align: center; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>⚖️ BMI計算機</h1>
    <form method="POST" action="/" id="bmiForm">
      <label for="height">身長（cm）</label>
      <input type="number" id="height" name="height" placeholder="例: 170" min="1" max="300" step="0.1">
      <label for="weight">体重（kg）</label>
      <input type="number" id="weight" name="weight" placeholder="例: 65" min="1" max="500" step="0.1">
      <div class="buttons">
        <button type="submit" class="btn-calc">計算する</button>
        <button type="button" class="btn-clear" onclick="clearForm()">クリア</button>
      </div>
    </form>
    {result_block}
    <p class="note">BMI = 体重(kg) ÷ 身長(m)²</p>
  </div>
  <script>
    function clearForm() {{
      document.getElementById('height').value = '';
      document.getElementById('weight').value = '';
      // 結果表示エリアを削除
      const r = document.querySelector('.result, .error');
      if (r) r.remove();
    }}
  </script>
</body>
</html>"""

# ── HTTPリクエストハンドラ ─────────────────────────────
class BMIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """アクセスログをシンプルに出力"""
        print(f"[{self.address_string()}] {format % args}")

    def send_html(self, html: str, status: int = 200):
        encoded = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(encoded))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        """GETリクエスト: トップページを表示"""
        if urlparse(self.path).path == "/":
            self.send_html(build_html())
        else:
            self.send_html("<h1>404 Not Found</h1>", 404)

    def do_POST(self):
        """POSTリクエスト: フォームデータを受け取りBMIを計算"""
        if urlparse(self.path).path != "/":
            self.send_html("<h1>404 Not Found</h1>", 404)
            return

        # リクエストボディを読み込む
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        params = parse_qs(body)

        try:
            height = float(params.get("height", ["0"])[0] or 0)
            weight = float(params.get("weight", ["0"])[0] or 0)
        except (ValueError, IndexError):
            height, weight = 0.0, 0.0

        if height <= 0 or weight <= 0:
            html = build_html(error="身長と体重に正の数値を入力してください")
        else:
            bmi, label = calc_bmi(height, weight)
            html = build_html(bmi=bmi, label=label)

        self.send_html(html)

# ── エントリーポイント ────────────────────────────────
if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), BMIHandler)
    print(f"サーバー起動中 → http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nサーバーを停止しました")
        server.server_close()