# -*- coding: utf-8 -*-

"""Upload and result pages for third-period task 3."""

import re


BASIC_NAMES = ["create", "insert", "search", "search_min", "delete_min", "delete"]
CHALLENGE_NAMES = ["dfs", "bfs"]


def add_task_title_style(html):
    extra_css = """
.period-with-week { display:inline-flex; align-items:flex-end; letter-spacing:-.08em; }
.period-main { display:inline-block; }
.period-week { display:inline-block; font-size:.63em; font-weight:950; line-height:1;
  margin-bottom:.10em; letter-spacing:-.06em; transform:translateX(-.04em); }
.task3-status-row { display:inline-flex; align-items:center; justify-content:flex-end;
  gap:8px; flex-shrink:0; }
.task3-status-row .status-pill, .task3-point-score { display:inline-flex;
  align-items:center; justify-content:center; padding:8px 12px; border-radius:999px;
  font-size:12px; font-weight:950; letter-spacing:.04em; line-height:1; white-space:nowrap; }
.task3-point-score { background:rgba(11,11,13,.06); color:rgba(11,11,13,.78); }
.challenge-section { margin-top:28px; padding-top:24px;
  border-top:1px dashed rgba(0,0,0,.15); }
.challenge-section .challenge-title {
  font-size:1.2rem;
  font-weight:900;
  color:#0f766e;
}
/* The outer card's state belongs to the basic questions. Keep the nested
   challenge block's colours tied to its own result instead. */
.challenge-section:not(.needs-review) .status-pill {
  background:rgba(37,138,89,.12); color:var(--poster-mint-dark); }
.challenge-section:not(.needs-review) .progress-bar {
  background:linear-gradient(90deg,var(--poster-mint-dark),var(--poster-mint)); }
.challenge-section:not(.needs-review) .issue-block {
  background:rgba(134,221,177,.22); border-color:rgba(37,138,89,.18); }
.challenge-section.needs-review .status-pill {
  background:var(--poster-alert-soft); color:#c63c1c; }
.challenge-section.needs-review .progress-bar {
  background:linear-gradient(90deg,var(--poster-alert),#ffba6a); }
.challenge-section.needs-review .issue-block {
  background:rgba(255,255,255,.58); border-color:rgba(11,11,13,.10); }
"""
    return html.replace("</style>", extra_css + "\n</style>", 1)


def replace_title(html):
    html = html.replace("Ocaml 1期", "OCaml 3期 課題3")
    html = html.replace("OCaml 1期", "OCaml 3期 課題3")
    return html.replace(
        "OCaml<br>1期",
        '<span>OCaml</span><br><span class="period-with-week">'
        '<span class="period-main">3期</span><span class="period-week">課題3</span></span>',
    )


def build_index_html(message=""):
    import web_app

    html = web_app.build_index_html(message)
    html = html.replace("href='/period'>選択画面へ戻る</a>",
                        "href='/period/3'>選択画面へ戻る</a>")
    html = html.replace("action='/check'", "action='/period/3/task3/check'")
    return add_task_title_style(replace_title(html))


def _filtered_summary(summary, names):
    questions = [q for q in summary.get("questions", []) if q.get("question") in names]
    counts = {status: sum(q.get("status") == status for q in questions)
              for status in ("OK", "WARNING", "NG", "ERROR")}
    return dict(summary, questions=questions, total=len(questions), ok=counts["OK"],
                warning=counts["WARNING"], ng=counts["NG"], error=counts["ERROR"])

def _is_unimplemented_challenge_question(question_summary):
    """Return True when dfs/bfs is absent and should not be shown."""
    question_name = question_summary.get("question")
    if question_name not in CHALLENGE_NAMES:
        return False

    results = question_summary.get("results", [])
    if not results:
        return False

    stderr_text = "\n".join(result.get("stderr", "") for result in results)
    return (
        all(result.get("status") == "ERROR" for result in results)
        and re.search(r"Unbound value\s+" + re.escape(question_name) + r"\b", stderr_text)
    )


def _challenge_summary(summary):
    questions = []
    for q in summary.get("questions", []):
        if q.get("question") not in CHALLENGE_NAMES:
            continue
        if _is_unimplemented_challenge_question(q):
            continue
        questions.append(q)

    counts = {status: sum(q.get("status") == status for q in questions)
              for status in ("OK", "WARNING", "NG", "ERROR")}

    return dict(summary, questions=questions, total=len(questions), ok=counts["OK"],
                warning=counts["WARNING"], ng=counts["NG"], error=counts["ERROR"])

def _add_points(article, score, total):
    label = "全問正解" if "<span class='status-pill'>全問正解</span>" in article else "確認が必要"
    marker = "<span class='status-pill'>{}</span>".format(label)
    replacement = ("<div class='task3-status-row'>{}"
                   "<span class='task3-point-score'>{}点/{}点</span></div>").format(
                       marker, score, total)
    return article.replace(marker, replacement, 1)


def _extract_articles(html):
    return re.findall(r"<article\s+class='[^']*'>.*?</article>", html, flags=re.S)


def _as_challenge_section(article):
    """Turn a rendered result card into a block for an existing result card."""
    match = re.match(r"<article\s+class='([^']*)'>(.*)</article>", article, flags=re.S)
    if not match:
        return ""
    state_class = " needs-review" if "needs-review" in match.group(1).split() else ""
    return "<section class='challenge-section{}'>{}</section>".format(
        state_class, match.group(2))


def build_result_html(all_results, file_summaries):
    import web_app

    basic_summaries = [_filtered_summary(summary, BASIC_NAMES) for summary in file_summaries]
    html = web_app.build_result_html(all_results, basic_summaries)
    basic_articles = _extract_articles(html)

    challenge_articles = []
    for summary in file_summaries:
        challenge = _challenge_summary(summary)
        if not challenge["questions"]:
            challenge_articles.append(None)
            continue
        rendered = web_app.build_result_html(all_results, [challenge])
        articles = _extract_articles(rendered)
        article = articles[0] if articles else ""
        # The basic block already identifies the submitted file; the nested block
        # gets the assignment-specified heading instead.
        article = re.sub(r"<h2 class='file-name[^']*'>.*?</h2>",
                         "<h2 class='file-name challenge-title'>チャレンジ問題</h2>", article,
                         count=1, flags=re.S)
        score = sum(q.get("status") == "OK" for q in challenge["questions"]) * 5
        challenge_articles.append(_as_challenge_section(_add_points(article, score, 10)))

    # Put each optional challenge block inside its file's one and only result card.
    for basic, challenge, summary in zip(basic_articles, challenge_articles, basic_summaries):
        score = sum(q.get("status") == "OK" for q in summary["questions"]) * 3
        decorated = _add_points(basic, score, 18)
        replacement = decorated.replace("</article>", (challenge or "") + "</article>", 1)
        html = html.replace(basic, replacement, 1)

    for label in BASIC_NAMES + CHALLENGE_NAMES:
        html = html.replace("Q" + label, label)
    return add_task_title_style(replace_title(html))
