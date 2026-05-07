from pathlib import Path
import subprocess
import tempfile
import csv
import os


SUBMISSION_DIR = Path("submissions")
RESULT_CSV = Path("result.csv")
RESULT_HTML = Path("result.html")


# =========================
# OCaml実行用
# =========================

def run_ocaml_code(code):
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".ml",
        delete=False,
        encoding="utf-8"
    ) as f:
        f.write(code)
        temp_path = f.name

    try:
        result = subprocess.run(
            ["ocaml", temp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        return result.stdout, result.stderr, result.returncode
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


def ocaml_path(path):
    return str(path.resolve()).replace("\\", "/")


# =========================
# 通常の値比較テスト
# =========================

def make_equal_test_code(submission_file, actual_expr, expected_expr):
    file_path = ocaml_path(submission_file)

    return '''
#use "{}";;

let print_result ok =
  if ok then
    print_endline "__RESULT__:OK"
  else
    print_endline "__RESULT__:NG"
;;

let actual = {};;
let expected = {};;

print_result (actual = expected);;
'''.format(file_path, actual_expr, expected_expr)


# =========================
# 例外チェック用テスト
# =========================

def make_exception_test_code(submission_file, actual_expr, expected_message):
    file_path = ocaml_path(submission_file)

    return '''
#use "{}";;

let print_result ok =
  if ok then
    print_endline "__RESULT__:OK"
  else
    print_endline "__RESULT__:NG"
;;

try
  let _ = {} in
  print_result false
with
| Failure msg -> print_result (msg = "{}")
| _ -> print_result false
;;
'''.format(file_path, actual_expr, expected_message)


# =========================
# 集合比較用テスト
# 18, 19, 20では順番が違っても同じ集合ならOKにする
# =========================

def make_set_equal_test_code(submission_file, actual_expr, expected_expr):
    file_path = ocaml_path(submission_file)

    return '''
#use "{}";;

let print_result ok =
  if ok then
    print_endline "__RESULT__:OK"
  else
    print_endline "__RESULT__:NG"
;;

let rec mem x lst =
  match lst with
  | [] -> false
  | y :: ys -> x = y || mem x ys
;;

let rec subset a b =
  match a with
  | [] -> true
  | x :: xs -> mem x b && subset xs b
;;

let set_equal a b =
  subset a b && subset b a
;;

let actual = {};;
let expected = {};;

print_result (set_equal actual expected);;
'''.format(file_path, actual_expr, expected_expr)


# =========================
# テスト定義
# =========================

TESTS = [
    # 1. checkl
    ("1-1 checkl", "equal", "checkl 3 [1; 2; 3; 4; 5; 6]", "true"),
    ("1-2 checkl", "equal", "checkl 1 [2; 3; 4; 5]", "false"),

    # 2. dellt
    ("2-1 dellt", "equal", "dellt 0 [1; 2; 3; 4]", "[1; 2; 3; 4]"),
    ("2-2 dellt", "equal", "dellt 1 [1; 2; 3; 4]", "[2; 3; 4]"),
    ("2-3 dellt", "equal", "dellt 2 [1; 2; 3; 4]", "[3; 4]"),
    ("2-4 dellt", "equal", "dellt 3 [1; 2; 3; 4]", "[4]"),
    ("2-5 dellt", "equal", "dellt 5 [1; 2; 3; 4]", "[]"),
    ("2-6 dellt", "equal",
     'dellt 3 ["A"; "B"; "C"; "D"; "E"; "F"]',
     '["D"; "E"; "F"]'),
    ("2-7 dellt negative", "exception", "dellt (-2) [1; 2]", "Error"),

    # 3. dellt2
    ("3-1 dellt2", "equal",
     'dellt2 1 ["A"; "B"; "C"; "D"; "E"; "F"]',
     '["B"; "C"; "D"; "E"; "F"]'),
    ("3-2 dellt2", "equal",
     'dellt2 3 ["A"; "B"; "C"; "D"; "E"; "F"]',
     '["A"; "B"; "D"; "E"; "F"]'),
    ("3-3 dellt2", "equal",
     "dellt2 3 [1; 2; 3; 4; 5; 6]",
     "[1; 2; 4; 5; 6]"),

    # 4. posl
    ("4-1 posl", "equal",
     'posl 3 ["AB"; "C"; "DEF"; "G"; "H"; "IJ"]',
     '"DEF"'),
    ("4-2 posl", "equal",
     "posl 2 [1; 2; 3; 4; 5]",
     "2"),
    ("4-3 posl exception", "exception",
     "posl 0 [1; 2; 3; 4; 5]",
     "Not Exist..."),

    # 5. add2list
    ("5-1 add2list", "equal",
     "add2list [1; 2]",
     "[3]"),
    ("5-2 add2list", "equal",
     "add2list [1; 2; 3]",
     "[3; 5]"),
    ("5-3 add2list", "equal",
     "add2list [1; 2; 3; 4; 5]",
     "[3; 5; 7; 9]"),

    # 6. mullist
    ("6-1 mullist", "equal",
     "mullist [1; 3; 5; 7] [2; 4; 6; 8]",
     "[2; 12; 30; 56]"),

    # 7. chglist
    ("7-1 chglist", "equal",
     'chglist ("A", "*") ["1"; "A"; "2"; "B"; "A"; "A"; "3"; "4"]',
     '["1"; "*"; "2"; "B"; "*"; "*"; "3"; "4"]'),

    # 8. replicate
    ("8-1 replicate", "equal",
     'replicate 3 ["A"]',
     '[["A"]; ["A"]; ["A"]]'),
    ("8-2 replicate", "equal",
     'replicate 5 "A"',
     '["A"; "A"; "A"; "A"; "A"]'),
    ("8-3 replicate", "equal",
     'replicate 3 ["1"; "#"]',
     '[["1"; "#"]; ["1"; "#"]; ["1"; "#"]]'),

    # 9. inslist
    ("9-1 inslist", "equal",
     'inslist 2 "*" ["A"; "B"; "C"; "D"; "E"]',
     '["A"; "*"; "B"; "C"; "D"; "E"]'),
    ("9-2 inslist", "equal",
     'inslist 6 "*" ["A"; "B"; "C"; "D"; "E"]',
     '["A"; "B"; "C"; "D"; "E"; "*"]'),
    ("9-3 inslist", "equal",
     'inslist 1 "+" []',
     '["+"]'),
    ("9-4 inslist", "equal",
     'inslist 1 "+" ["A"]',
     '["+"; "A"]'),
    ("9-5 inslist exception", "exception",
     'inslist 0 "+" ["A"]',
     "Error"),

    # 10. merge
    ("10-1 merge", "equal",
     "merge [1; 2; 3] [4; 5; 6]",
     "[1; 4; 2; 5; 3; 6]"),
    ("10-2 merge", "equal",
     'merge ["A"; "B"] ["C"; "D"; "EF"; "GH"]',
     '["A"; "C"; "B"; "D"; "EF"; "GH"]'),

    # 11. inside_length
    ("11-1 inside_length", "equal",
     "inside_length [[1; 2; 3]; [4; 5]; [6]; [7; 8; 9; 10]]",
     "10"),
    ("11-2 inside_length", "equal",
     'inside_length [["A"; "B"]; ["C"; "D"]; ["EF"; "GH"]]',
     "6"),

    # 12. concat
    ("12-1 concat", "equal",
     "concat [[0; 3; 4]; [2]; [0]; [5; 0]]",
     "[0; 3; 4; 2; 0; 5; 0]"),

    # 13. assoc
    ("13-1 assoc", "equal",
     "assoc 33 [(3, 4); (33, 5); (11, 2); (55, 1)]",
     "5"),
    ("13-2 assoc", "equal",
     "assoc 2 [(3, 4); (33, 5); (11, 2); (55, 1)]",
     "11"),
    ("13-3 assoc", "equal",
     'assoc "03" [("Kyoto", "075"); ("Osaka", "06"); ("Tokyo", "03")]',
     '"Tokyo"'),
    ("13-4 assoc", "equal",
     'assoc "Kyoto" [("Kyoto", "075"); ("Osaka", "06"); ("Tokyo", "03")]',
     '"075"'),
    ("13-5 assoc exception", "exception",
     "assoc 6 [(3, 4); (33, 5); (11, 2); (55, 1)]",
     "Not found..."),

    # 14. minimum
    ("14-1 minimum", "equal",
     "minimum [3; 2; 5; 1]",
     "1"),
    ("14-2 minimum", "equal",
     'minimum ["abc"; "sdf"]',
     '"abc"'),
    ("14-3 minimum exception", "exception",
     "minimum []",
     "Error"),

    # 15. extract
    ("15-1 extract", "equal",
     "extract (fun x -> x > 10) [21; 2; 31; 1]",
     "[21; 31]"),

    # 16. index
    ("16-1 index", "equal",
     "index [21; 2; 31; 1] 21",
     "0"),
    ("16-2 index", "equal",
     "index ['a'; '3'; 'b'; 'z'; '1'] 'z'",
     "3"),

    # 17. numOfRotes
    ("17-1 numOfRotes", "equal",
     "numOfRotes (5, 4)",
     "126"),

    # 18. inter
    # 集合なので順番は問わない
    ("18-1 inter", "set_equal",
     "inter [1; 2; 3] [2; 3; 4]",
     "[2; 3]"),
    ("18-2 inter", "set_equal",
     'inter ["A"; "B"; "C"] ["B"; "D"]',
     '["B"]'),
    ("18-3 inter", "set_equal",
     "inter [1; 2] [3; 4]",
     "[]"),

    # 19. union
    # 集合なので順番は問わない
    ("19-1 union", "set_equal",
     "union [1; 2; 3] [3; 4; 5]",
     "[1; 2; 3; 4; 5]"),
    ("19-2 union", "set_equal",
     'union ["A"; "B"] ["B"; "C"]',
     '["A"; "B"; "C"]'),
    ("19-3 union", "set_equal",
     "union [] [1; 2]",
     "[1; 2]"),

    # 20. diff
    # 集合なので順番は問わない
    ("20-1 diff", "set_equal",
     "diff [1; 2; 3; 4] [2; 4]",
     "[1; 3]"),
    ("20-2 diff", "set_equal",
     'diff ["A"; "B"; "C"] ["B"]',
     '["A"; "C"]'),
    ("20-3 diff", "set_equal",
     "diff [1; 2] [1; 2]",
     "[]"),
]


# =========================
# テスト実行
# =========================

def run_one_test(submission_file, test):
    name, mode, actual_expr, expected = test

    if mode == "equal":
        code = make_equal_test_code(submission_file, actual_expr, expected)
    elif mode == "exception":
        code = make_exception_test_code(submission_file, actual_expr, expected)
    elif mode == "set_equal":
        code = make_set_equal_test_code(submission_file, actual_expr, expected)
    else:
        raise ValueError("Unknown test mode: {}".format(mode))

    stdout, stderr, returncode = run_ocaml_code(code)

    if "__RESULT__:OK" in stdout:
        status = "OK"
    elif "__RESULT__:NG" in stdout:
        status = "NG"
    else:
        status = "ERROR"

    return {
        "file": submission_file.name,
        "test": name,
        "status": status,
        "stdout": stdout.strip(),
        "stderr": stderr.strip(),
    }

def get_question_no(test_name):
    """
    '2-7 dellt negative' から '2' を取り出す。
    '17-1 numOfRotes' から '17' を取り出す。
    """
    first_part = test_name.split()[0]
    question_no = first_part.split("-")[0]
    return question_no

def summarize_by_question(results):
    """
    54個の小テスト結果を、1〜20の大問単位にまとめる。
    大問内のすべての小テストがOKならOK。
    1つでもNGまたはERRORがあればNG。
    """
    summaries = []

    for q in range(1, 21):
        q_str = str(q)
        q_results = []

        for result in results:
            if get_question_no(result["test"]) == q_str:
                q_results.append(result)

        if not q_results:
            summaries.append({
                "question": q_str,
                "status": "NG",
                "ok": 0,
                "ng": 0,
                "error": 0,
                "total": 0,
            })
            continue

        ok_count = 0
        ng_count = 0
        error_count = 0

        for result in q_results:
            if result["status"] == "OK":
                ok_count += 1
            elif result["status"] == "NG":
                ng_count += 1
            else:
                error_count += 1

        if ok_count == len(q_results):
            status = "OK"
        else:
            status = "NG"

        summaries.append({
            "question": q_str,
            "status": status,
            "ok": ok_count,
            "ng": ng_count,
            "error": error_count,
            "total": len(q_results),
        })

    return summaries

# =========================
# HTML出力用
# =========================

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


def write_html_report(all_results, file_summaries):
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
    html.append("<title>OCaml課題チェッカー結果</title>")
    html.append("""
<style>
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #f5f7fb;
  color: #222;
  margin: 0;
  padding: 32px;
}

h1 {
  margin-bottom: 8px;
}

.description {
  color: #555;
  margin-bottom: 24px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.summary-card h2 {
  font-size: 18px;
  margin: 0 0 12px;
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
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 28px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
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
</style>
""")
    html.append("</head>")
    html.append("<body>")

    html.append("<h1>OCaml課題チェッカー結果</h1>")
    html.append("<p class='description'>提出された .ml ファイルに対して、各実行例の結果を自動チェックした結果です。</p>")

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

            row_class = ""
            status_class = ""

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

    html.append("</body>")
    html.append("</html>")

    with RESULT_HTML.open("w", encoding="utf-8") as f:
        f.write("\n".join(html))


def run_checker():
    if not SUBMISSION_DIR.exists():
        print("{} フォルダがありません。".format(SUBMISSION_DIR))
        return

    ml_files = sorted(SUBMISSION_DIR.glob("*.ml"))

    if not ml_files:
        print("{} に .ml ファイルがありません。".format(SUBMISSION_DIR))
        return

    all_results = []
    file_summaries = []

    for ml_file in ml_files:
        print("=" * 60)
        print("Checking: {}".format(ml_file.name))

        ok_count = 0
        ng_count = 0
        error_count = 0

        for test in TESTS:
            result = run_one_test(ml_file, test)
            all_results.append(result)

            status = result["status"]
            test_name = result["test"]

            if status == "OK":
                ok_count += 1
                print("[OK]    {}".format(test_name))
            elif status == "NG":
                ng_count += 1
                print("[NG]    {}".format(test_name))
            else:
                error_count += 1
                print("[ERROR] {}".format(test_name))

        total = ok_count + ng_count + error_count

        print("-" * 60)
        print("Result: OK {} / {}, NG {}, ERROR {}".format(
            ok_count, total, ng_count, error_count
        ))

        file_summaries.append({
            "file": ml_file.name,
            "ok": ok_count,
            "ng": ng_count,
            "error": error_count,
            "total": total,
        })

    with RESULT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["file", "test", "status", "stdout", "stderr"]
        )
        writer.writeheader()
        writer.writerows(all_results)

    write_html_report(all_results, file_summaries)

    print("=" * 60)
    print("CSV出力完了: {}".format(RESULT_CSV))
    print("HTML出力完了: {}".format(RESULT_HTML))


if __name__ == "__main__":
    run_checker()
