"""Upload and result presentation for fourth-period SProlog."""

import re
from .checker import QUESTION_POINTS, TOTAL_POINTS

LABELS = {
    "1-1-cid-reserved": "問1-1 CID/予約語", "1-2-vid": "問1-2 VID", "1-3-num": "問1-3 NUM", "1-4-to": "問1-4 TO",
    "2-1-terms-right-recursion": "問2-1 terms右再帰", "2-2-args-right-recursion": "問2-2 args右再帰",
    "3-1-clause": "問3-1 clause", "3-2-to-opt": "問3-2 to_opt", "3-3-command": "問3-3 command",
    "3-4-term": "問3-4 term", "3-5-terms": "問3-5 terms", "3-6-predicate": "問3-6 predicate",
    "3-7-args": "問3-7 args", "3-8-expr": "問3-8 expr", "3-9-tail-opt": "問3-9 tail_opt",
    "3-10-list": "問3-10 list", "3-11-id": "問3-11 id", "5-multiple-goals": "問5 複数述語",
    "6-1-line-count": "問6-1 改行カウント", "6-2-error-handle": "問6-2 エラー処理",
    "7-1-arithmexp": "問7-1 arithmexp", "7-2-expr-uses-arithmexp": "問7-2 exprからarithmexp",
    "8-is-arithmexp": "問8 VID IS arithmexp",
}

STYLE = """
.period-with-week{display:inline-flex;align-items:flex-end;gap:.04em;letter-spacing:-.08em}
.period-main{display:inline-block}.period-week{display:inline-block;font-size:.63em;font-weight:950;line-height:1;margin-bottom:.10em;letter-spacing:-.06em;transform:none}
.fourth-status-row{display:inline-flex;align-items:center;gap:8px}.fourth-point-score{padding:8px 12px;border-radius:999px;background:rgba(11,11,13,.06);font-size:12px;font-weight:950;white-space:nowrap}
.fourth-manual-check-note{display:block;margin-top:14px;color:rgba(11,11,13,.76);font-size:inherit;font-weight:inherit;line-height:inherit}
"""

TASK_GUIDE = """<ul class='guide-list'>%s</ul>""" % "".join(
    "<li class='guide-card'><p class='guide-card-title'>%s</p></li>" % item for item in (
        "問1：字句解析器の実装", "問2：terms / args の右再帰化", "問3：構文解析器の空欄補充",
        "問4：isono.pl での動作確認", "問5：複数述語の質問対応", "問6：行番号付き構文エラー表示",
        "問7：算術式 arithmexp の追加", "問8：VID IS arithmexp の追加"))
CRITERIA_GUIDE = """<div class='guide-card'><p class='guide-card-title'>配点</p><ul class='guide-submit-list'>
<li>問1：20点</li><li>問2：10点</li><li>問3：22点</li><li>問4：8点（自動採点対象外）</li>
<li>問5：10点</li><li>問6：10点</li><li>問7：10点</li><li>問8：10点</li>
<li>自動採点対象は問1,2,3,5,6,7,8 の92点</li><li>問5以降に実行結果がない場合は各問5点減点</li></ul></div>"""


def _decorate(html):
    html = html.replace("Ocaml 1期", "OCaml 4期").replace("OCaml 1期", "OCaml 4期")
    html = html.replace("OCaml<br>1期", '<span>OCaml</span><br><span class="period-with-week"><span class="period-main">4期</span><span class="period-week"></span></span>')
    html = html.replace("</style>", STYLE + "</style>", 1)
    html = re.sub(r"const taskGuideHtml = `.*?`;", "const taskGuideHtml = `" + TASK_GUIDE + "`;", html, count=1, flags=re.S)
    html = re.sub(r"const criteriaGuideHtml = `.*?`;", "const criteriaGuideHtml = `" + CRITERIA_GUIDE + "`;", html, count=1, flags=re.S)
    return html


def build_index_html(message=""):
    import web_app
    html = web_app.build_index_html(message)
    html = html.replace("action='/check'", "action='/period/4/check'")
    return _decorate(html)


def build_result_html(all_results, file_summaries):
    import web_app
    html = web_app.build_result_html(all_results, file_summaries)

    html = html.replace(
        "採点結果と確認が必要な問を、ファイルごとにまとめて表示しています。",
        "採点結果と確認が必要な問を、ファイルごとにまとめて表示しています。"
        "<span class='fourth-manual-check-note'>"
        "問題4「isono.plを用いて振舞いを確認しなさい．」は自動採点できないため、提出PDFで確認してください。"
        "</span>"
    )

    articles = re.findall(r"<article\s+class='[^']*'>.*?</article>", html, re.S)

    for article, summary in zip(articles, file_summaries):
        score = sum(
            QUESTION_POINTS.get(q["question"], 0)
            for q in summary["questions"]
            if q["status"] == "OK"
        )

        label = "全問正解" if "<span class='status-pill'>全問正解</span>" in article else "確認が必要"
        marker = "<span class='status-pill'>%s</span>" % label

        badge = (
            "<div class='fourth-status-row'>"
            "%s"
            "<span class='fourth-point-score'>%d点/%d点</span>"
            "</div>"
        ) % (marker, score, TOTAL_POINTS)

        decorated = article.replace(marker, badge, 1)
        html = html.replace(article, decorated, 1)

    for key, label in LABELS.items():
        html = html.replace("Q" + key, label)

    return _decorate(html)