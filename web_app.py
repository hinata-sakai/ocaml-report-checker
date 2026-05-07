# -*- coding: utf-8 -*-

from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import tempfile
import shutil
import cgi
import sys
import traceback

import run_checker


HOST = "127.0.0.1"
PORT = 8000


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
}

.upload-box {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

input[type="file"] {
  display: block;
  margin: 16px 0;
  padding: 12px;
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
  margin-top: 12px;
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
    html.append("<p class='description'>アップロードされた .ml ファイルに対して、各実行例の結果を自動チェックします。</p>")
    html.append("</div>")

    html.append("<a class='back-link' href='/'>← 別のファイルをチェックする</a>")

    html.append("<div class='summary-grid'>")
    for summary in file_summaries:
        filename = html_escape(summary["file"])
        ok = summary["ok"]
        ng = summary["ng"]
        error = summary["error"]
        total = summary["total"]

        html.append("<div class='summary-card'>")
        html.append("<h2>{}</h2>".format(filename))
        html.append("<div class='score'>OK {} / {}</div>".format(ok, total))
        html.append("<div><span class='ok'>OK</span>: {}</div>".format(ok))
        html.append("<div><span class='ng'>NG</span>: {}</div>".format(ng))
        html.append("<div><span class='error'>ERROR</span>: {}</div>".format(error))
        html.append("</div>")
    html.append("</div>")

    for summary in file_summaries:
        filename = summary["file"]

        html.append("<div class='file-section'>")
        html.append("<h2>{}</h2>".format(html_escape(filename)))
        html.append("<p>OK: {} / {}　NG: {}　ERROR: {}</p>".format(
            summary["ok"],
            summary["total"],
            summary["ng"],
            summary["error"]
        ))

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
        ok_count = 0
        ng_count = 0
        error_count = 0

        for test in run_checker.TESTS:
            result = run_checker.run_one_test(ml_file, test)
            all_results.append(result)

            status = result["status"]

            if status == "OK":
                ok_count += 1
            elif status == "NG":
                ng_count += 1
            else:
                error_count += 1

        total = ok_count + ng_count + error_count

        file_summaries.append({
            "file": ml_file.name,
            "ok": ok_count,
            "ng": ng_count,
            "error": error_count,
            "total": total,
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

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            self.send_html(build_index_html())
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
