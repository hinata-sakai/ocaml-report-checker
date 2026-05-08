# -*- coding: utf-8 -*-

from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import tempfile
import shutil
import cgi
import traceback

import run_checker


HOST = "127.0.0.1"
PORT = 8000
BACKGROUND_IMAGE = Path("webhaikei.png")


def html_escape(s):
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_result_html(all_results, file_summaries):
    rows_by_file = {}

    for result in all_results:
        filename = result["file"]
        if filename not in rows_by_file:
            rows_by_file[filename] = []
        rows_by_file[filename].append(result)

    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='ja'>")
    html.append("<head>")
    html.append("<meta charset='UTF-8'>")
    html.append("<title>OCaml課題チェッカー Web版</title>")
    html.append("""
<style>
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #f5f7fb;
  color: #222;
  margin: 0;
  padding: 32px;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
}

.header {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

h1 {
  margin: 0 0 8px;
}

.description {
  color: #555;
  margin: 0;
  line-height: 1.7;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.summary-card {
  background: white;
  border-radius: 14px;
  padding: 18px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.summary-card h2 {
  font-size: 18px;
  margin: 0 0 12px;
  word-break: break-all;
}

.score {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

.ok {
  color: #0a7f36;
  font-weight: bold;
}

.ng {
  color: #b77900;
  font-weight: bold;
}

.error {
  color: #c62828;
  font-weight: bold;
}

.file-section {
  background: white;
  border-radius: 14px;
  padding: 20px;
  margin-bottom: 28px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.section-title {
  margin-top: 28px;
  margin-bottom: 8px;
  font-size: 18px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}

th, td {
  border-bottom: 1px solid #e5e7eb;
  padding: 10px;
  text-align: left;
  vertical-align: top;
}

th {
  background: #f0f2f5;
}

.status-ok {
  background: #e8f5e9;
}

.status-ng {
  background: #fff8e1;
}

.status-error {
  background: #ffebee;
}

details {
  margin-top: 4px;
}

pre {
  white-space: pre-wrap;
  word-break: break-word;
  background: #f6f8fa;
  padding: 8px;
  border-radius: 8px;
  font-size: 13px;
}

.back-link {
  display: inline-block;
  margin-bottom: 20px;
  color: #2563eb;
  text-decoration: none;
  font-weight: bold;
}
</style>
""")
    html.append("</head>")
    html.append("<body>")
    html.append("<div class='container'>")

    html.append("<div class='header'>")
    html.append("<h1>OCaml課題チェッカー Web版</h1>")
    html.append("<p class='description'>")
    html.append("アップロードされた .ml ファイルに対して、各大問ごとに OK / NG を判定します。")
    html.append("大問内の小テストがすべてOKなら大問OK、1つでもNGまたはERRORがあれば大問NGです。")
    html.append("</p>")
    html.append("</div>")

    html.append("<a class='back-link' href='/upload'>← 別のファイルをチェックする</a>")

    html.append("<div class='summary-grid'>")
    for summary in file_summaries:
        filename = html_escape(summary["file"])
        ok = summary["ok"]
        ng = summary["ng"]
        total = summary["total"]

        html.append("<div class='summary-card'>")
        html.append("<h2>{}</h2>".format(filename))
        html.append("<div class='score'>大問OK {} / {}</div>".format(ok, total))
        html.append("<div><span class='ok'>大問OK</span>: {}</div>".format(ok))
        html.append("<div><span class='ng'>大問NG</span>: {}</div>".format(ng))
        html.append("</div>")
    html.append("</div>")

    for summary in file_summaries:
        filename = summary["file"]
        question_summaries = summary.get("questions", [])

        html.append("<div class='file-section'>")
        html.append("<h2>{}</h2>".format(html_escape(filename)))
        html.append("<p>大問OK: {} / {}　大問NG: {}</p>".format(
            summary["ok"],
            summary["total"],
            summary["ng"]
        ))

        html.append("<h3 class='section-title'>大問ごとの判定</h3>")
        html.append("<table>")
        html.append("<tr>")
        html.append("<th>大問</th>")
        html.append("<th>判定</th>")
        html.append("<th>小テスト結果</th>")
        html.append("</tr>")

        for q_summary in question_summaries:
            q = q_summary["question"]
            status = q_summary["status"]
            ok_count = q_summary["ok"]
            ng_count = q_summary["ng"]
            error_count = q_summary["error"]
            total_count = q_summary["total"]

            if status == "OK":
                row_class = "status-ok"
                status_class = "ok"
            else:
                row_class = "status-ng"
                status_class = "ng"

            html.append("<tr class='{}'>".format(row_class))
            html.append("<td>Question {}</td>".format(html_escape(q)))
            html.append("<td class='{}'>{}</td>".format(status_class, html_escape(status)))
            html.append("<td>OK {}/{}　NG {}　ERROR {}</td>".format(
                ok_count,
                total_count,
                ng_count,
                error_count
            ))
            html.append("</tr>")

        html.append("</table>")

        html.append("<h3 class='section-title'>小テストごとの詳細</h3>")
        html.append("<table>")
        html.append("<tr>")
        html.append("<th>テスト</th>")
        html.append("<th>結果</th>")
        html.append("<th>詳細</th>")
        html.append("</tr>")

        for result in rows_by_file.get(filename, []):
            status = result["status"]
            test_name = result["test"]
            stdout = result["stdout"]
            stderr = result["stderr"]

            if status == "OK":
                row_class = "status-ok"
                status_class = "ok"
            elif status == "NG":
                row_class = "status-ng"
                status_class = "ng"
            else:
                row_class = "status-error"
                status_class = "error"

            detail = ""
            if stdout or stderr:
                detail += "<details><summary>stdout / stderr を表示</summary>"
                if stdout:
                    detail += "<p>stdout</p><pre>{}</pre>".format(html_escape(stdout))
                if stderr:
                    detail += "<p>stderr</p><pre>{}</pre>".format(html_escape(stderr))
                detail += "</details>"
            else:
                detail = "-"

            html.append("<tr class='{}'>".format(row_class))
            html.append("<td>{}</td>".format(html_escape(test_name)))
            html.append("<td class='{}'>{}</td>".format(status_class, html_escape(status)))
            html.append("<td>{}</td>".format(detail))
            html.append("</tr>")

        html.append("</table>")
        html.append("</div>")

    html.append("</div>")
    html.append("</body>")
    html.append("</html>")

    return "\n".join(html)


def build_start_html():
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='ja'>")
    html.append("<head>")
    html.append("<meta charset='UTF-8'>")
    html.append("<title>OCaml課題チェッカー</title>")
    html.append("""
<style>
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: white;
  background: #020817;
}

/* 背景画像レイヤー */
.space-bg {
  position: fixed;
  inset: 0;
  background-image: url('/background.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  transform: scale(1.05);
  animation: slowGalaxyMove 30s ease-in-out infinite alternate;
  z-index: 0;
}

/* 背景を少し暗くして文字を読みやすくする */
.dark-overlay {
  position: fixed;
  inset: 0;
  background:
    radial-gradient(circle at center, rgba(0, 0, 0, 0.10), rgba(0, 0, 0, 0.42)),
    linear-gradient(rgba(0, 0, 0, 0.18), rgba(0, 0, 0, 0.32));
  z-index: 1;
}

/* 星のきらめきレイヤー */
.stars {
  position: fixed;
  inset: 0;
  z-index: 2;
  pointer-events: none;
}

.star {
  position: absolute;
  width: 3px;
  height: 3px;
  background: white;
  border-radius: 50%;
  opacity: 0.2;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
  animation: twinkle 4s ease-in-out infinite;
}

.star.s1  { top: 12%; left: 18%; animation-delay: 0s; }
.star.s2  { top: 18%; left: 72%; animation-delay: 1.3s; }
.star.s3  { top: 26%; left: 46%; animation-delay: 2.1s; }
.star.s4  { top: 35%; left: 82%; animation-delay: 0.7s; }
.star.s5  { top: 45%; left: 20%; animation-delay: 3.2s; }
.star.s6  { top: 56%; left: 62%; animation-delay: 1.8s; }
.star.s7  { top: 68%; left: 30%; animation-delay: 2.8s; }
.star.s8  { top: 76%; left: 78%; animation-delay: 0.4s; }
.star.s9  { top: 84%; left: 52%; animation-delay: 3.7s; }
.star.s10 { top: 22%; left: 10%; animation-delay: 2.5s; }
.star.s11 { top: 62%; left: 88%; animation-delay: 1.1s; }
.star.s12 { top: 8%;  left: 55%; animation-delay: 3.4s; }
.star.s13 { top: 15%; left: 34%; animation-delay: 0.9s; }
.star.s14 { top: 31%; left: 66%; animation-delay: 2.9s; }
.star.s15 { top: 41%; left: 12%; animation-delay: 1.6s; }
.star.s16 { top: 50%; left: 73%; animation-delay: 3.9s; }
.star.s17 { top: 60%; left: 43%; animation-delay: 0.2s; }
.star.s18 { top: 72%; left: 15%; animation-delay: 2.2s; }
.star.s19 { top: 82%; left: 67%; animation-delay: 1.4s; }
.star.s20 { top: 10%; left: 86%; animation-delay: 3.1s; }

/* 流れ星レイヤー */
.shooting-star {
  position: fixed;
  top: 18%;
  right: -180px;
  width: 160px;
  height: 2px;
  background: linear-gradient(90deg, rgba(255,255,255,0.95), rgba(255,255,255,0));
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.9);
  transform: rotate(-35deg);
  opacity: 0;
  z-index: 3;
  animation: shootingStar 10s ease-in-out infinite;
  pointer-events: none;
}

.shooting-star.second {
  top: 58%;
  right: -200px;
  width: 125px;
  animation-delay: 5.5s;
  animation-duration: 13s;
  opacity: 0;
}

/* 文字とボタン */
.start-screen {
  position: relative;
  z-index: 4;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  text-align: center;
}

.content {
  margin-top: 70px;
}

.school {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.4;
  margin-bottom: 55px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.55);
}

.title {
  font-size: 40px;
  font-weight: 800;
  line-height: 1.35;
  color: #ff5a00;
  margin-bottom: 35px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.65);
}

.year {
  font-size: 44px;
  font-weight: 800;
  color: #ff5a00;
  letter-spacing: 6px;
  margin-bottom: 90px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.65);
}

.start-button {
  display: inline-block;
  background: #31148f;
  color: white;
  text-decoration: none;
  font-size: 28px;
  font-weight: 800;
  padding: 10px 70px;
  min-width: 260px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.35);
  transition: transform 0.25s ease, background 0.25s ease, box-shadow 0.25s ease;
}

.start-button:hover {
  background: #4320b8;
  transform: translateY(-2px);
  box-shadow: 0 8px 22px rgba(0,0,0,0.45), 0 0 18px rgba(120, 90, 255, 0.45);
}

/* 背景画像のゆっくりした動き */
@keyframes slowGalaxyMove {
  0% {
    transform: scale(1.05) translate3d(0, 0, 0);
  }
  50% {
    transform: scale(1.10) translate3d(-18px, 10px, 0);
  }
  100% {
    transform: scale(1.07) translate3d(16px, -10px, 0);
  }
}

/* 星の明滅 */
@keyframes twinkle {
  0%, 100% {
    opacity: 0.18;
    transform: scale(0.8);
  }
  45% {
    opacity: 0.95;
    transform: scale(1.35);
  }
  70% {
    opacity: 0.35;
    transform: scale(1.0);
  }
}

/* 流れ星 */
@keyframes shootingStar {
  0% {
    opacity: 0;
    transform: translate3d(0, 0, 0) rotate(-35deg);
  }
  6% {
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  22% {
    opacity: 0;
    transform: translate3d(-900px, 520px, 0) rotate(-35deg);
  }
  100% {
    opacity: 0;
    transform: translate3d(-900px, 520px, 0) rotate(-35deg);
  }
}

@media (max-width: 700px) {
  .content {
    margin-top: 50px;
    padding: 0 20px;
  }

  .school {
    font-size: 22px;
  }

  .title {
    font-size: 30px;
  }

  .year {
    font-size: 34px;
    margin-bottom: 60px;
  }

  .start-button {
    font-size: 22px;
    padding: 12px 42px;
  }
}
</style>
""")
    html.append("</head>")
    html.append("<body>")
    html.append("<div class='space-bg'></div>")
    html.append("<div class='dark-overlay'></div>")

    html.append("<div class='stars'>")
    html.append("<span class='star s1'></span>")
    html.append("<span class='star s2'></span>")
    html.append("<span class='star s3'></span>")
    html.append("<span class='star s4'></span>")
    html.append("<span class='star s5'></span>")
    html.append("<span class='star s6'></span>")
    html.append("<span class='star s7'></span>")
    html.append("<span class='star s8'></span>")
    html.append("<span class='star s9'></span>")
    html.append("<span class='star s10'></span>")
    html.append("<span class='star s11'></span>")
    html.append("<span class='star s12'></span>")
    html.append("<span class='star s13'></span>")
    html.append("<span class='star s14'></span>")
    html.append("<span class='star s15'></span>")
    html.append("<span class='star s16'></span>")
    html.append("<span class='star s17'></span>")
    html.append("<span class='star s18'></span>")
    html.append("<span class='star s19'></span>")
    html.append("<span class='star s20'></span>")
    html.append("</div>")

    html.append("<div class='shooting-star'></div>")
    html.append("<div class='shooting-star second'></div>")

    html.append("<div class='start-screen'>")
    html.append("<div class='content'>")
    html.append("<div class='school'>東京理科大学 創域理工学部<br>情報計算科学科</div>")
    html.append("<div class='title'>計算機科学基礎実験<br>計算機科学基礎演習</div>")
    html.append("<div class='year'>2026</div>")
    html.append("<a class='start-button' href='/upload'>採点をはじめる</a>")
    html.append("</div>")
    html.append("</div>")
    html.append("</body>")
    html.append("</html>")

    return "\n".join(html)


def build_index_html(message=""):
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='ja'>")
    html.append("<head>")
    html.append("<meta charset='UTF-8'>")
    html.append("<title>OCaml課題チェッカー Web版</title>")
    html.append("""
<style>
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #f5f7fb;
  color: #222;
  margin: 0;
  padding: 32px;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

h1 {
  margin: 0 0 12px;
}

.description {
  color: #555;
  line-height: 1.7;
}

input[type="file"] {
  display: block;
  margin: 20px 0;
  padding: 14px;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  background: #fff;
  width: 100%;
  box-sizing: border-box;
}

button {
  background: #2563eb;
  color: white;
  border: none;
  padding: 12px 18px;
  border-radius: 10px;
  font-size: 15px;
  cursor: pointer;
  font-weight: bold;
}

button:hover {
  background: #1d4ed8;
}

.note {
  color: #666;
  font-size: 14px;
  margin-top: 16px;
  line-height: 1.7;
}

.message {
  color: #c62828;
  font-weight: bold;
  margin-top: 16px;
}
</style>
""")
    html.append("</head>")
    html.append("<body>")
    html.append("<div class='container'>")
    html.append("<div class='card'>")
    html.append("<h1>OCaml課題チェッカー Web版</h1>")
    html.append("<p class='description'>")
    html.append("課題の .ml ファイルをアップロードすると、checkl から diff までの実行例を自動でチェックします。")
    html.append("判定は大問単位で行い、大問内の小テストがすべてOKなら大問OK、1つでもNGまたはERRORがあれば大問NGになります。")
    html.append("複数の .ml ファイルを同時に選択できます。")
    html.append("</p>")

    if message:
        html.append("<p class='message'>{}</p>".format(html_escape(message)))

    html.append("<form method='POST' enctype='multipart/form-data' action='/check'>")
    html.append("<input type='file' name='files' accept='.ml' multiple required>")
    html.append("<button type='submit'>チェック実行</button>")
    html.append("</form>")

    html.append("<p class='note'>")
    html.append("注意: Exception が出る実行例を提出ファイル内で直接実行している場合、読み込み時点で ERROR になることがあります。")
    html.append("課題文の指示通り、例外が出る呼び出しはコメントアウトしてください。")
    html.append("</p>")

    html.append("</div>")
    html.append("</div>")
    html.append("</body>")
    html.append("</html>")

    return "\n".join(html)


def check_uploaded_files(upload_dir):
    all_results = []
    file_summaries = []

    ml_files = sorted(upload_dir.glob("*.ml"))

    for ml_file in ml_files:
        file_results = []

        # まずは54個の小テストをすべて実行する
        for test in run_checker.TESTS:
            result = run_checker.run_one_test(ml_file, test)
            all_results.append(result)
            file_results.append(result)

        # 小テスト結果を1〜20の大問単位にまとめる
        question_summaries = run_checker.summarize_by_question(file_results)

        question_ok_count = 0
        question_ng_count = 0

        for summary in question_summaries:
            if summary["status"] == "OK":
                question_ok_count += 1
            else:
                question_ng_count += 1

        question_total = question_ok_count + question_ng_count

        file_summaries.append({
            "file": ml_file.name,
            "ok": question_ok_count,
            "ng": question_ng_count,
            "error": 0,
            "total": question_total,
            "questions": question_summaries,
        })

    return all_results, file_summaries


class CheckerHandler(BaseHTTPRequestHandler):
    def send_html(self, html, status=200):
        data = html.encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_png(self, path):
        if not path.exists():
            self.send_response(404)
            self.end_headers()
            return

        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            self.send_html(build_start_html())
        elif self.path == "/upload" or self.path.startswith("/upload?"):
            self.send_html(build_index_html())
        elif self.path == "/background.png":
            self.send_png(BACKGROUND_IMAGE)
        else:
            self.send_html(build_index_html("ページが見つかりません。"), status=404)

    def do_POST(self):
        if self.path != "/check":
            self.send_html(build_index_html("不正なURLです。"), status=404)
            return

        temp_dir = None

        try:
            content_type = self.headers.get("Content-Type")

            if not content_type:
                self.send_html(build_index_html("ファイルが送信されていません。"), status=400)
                return

            temp_dir = Path(tempfile.mkdtemp(prefix="ocaml_upload_"))

            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    "REQUEST_METHOD": "POST",
                    "CONTENT_TYPE": content_type,
                }
            )

            if "files" not in form:
                self.send_html(build_index_html(".ml ファイルを選択してください。"), status=400)
                return

            uploaded_items = form["files"]

            if not isinstance(uploaded_items, list):
                uploaded_items = [uploaded_items]

            saved_count = 0

            for item in uploaded_items:
                filename = Path(item.filename or "").name

                if not filename:
                    continue

                if not filename.endswith(".ml"):
                    continue

                save_path = temp_dir / filename

                with save_path.open("wb") as f:
                    shutil.copyfileobj(item.file, f)

                saved_count += 1

            if saved_count == 0:
                self.send_html(build_index_html(".ml ファイルがアップロードされていません。"), status=400)
                return

            all_results, file_summaries = check_uploaded_files(temp_dir)

            html = build_result_html(all_results, file_summaries)
            self.send_html(html)

        except Exception:
            err = traceback.format_exc()
            html = build_index_html("実行中にエラーが発生しました。")
            html += "<pre>{}</pre>".format(html_escape(err))
            self.send_html(html, status=500)

        finally:
            if temp_dir is not None and temp_dir.exists():
                shutil.rmtree(str(temp_dir))


def main():
    server = HTTPServer((HOST, PORT), CheckerHandler)

    print("OCaml課題チェッカー Web版を起動しました。")
    print("URL: http://{}:{}".format(HOST, PORT))
    print("終了するには Ctrl + C を押してください。")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("終了します。")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()