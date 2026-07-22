# -*- coding: utf-8 -*-

"""Upload and result pages for third-period task 1."""

THIRD_TASK1_AUTO_POINTS = {
    "create": 2, "unshift": 2, "shift": 2, "push": 2, "pop": 2,
    "size": 2, "max": 2, "min": 2, "get": 2, "indexOf": 2,
    "set": 2, "remove": 2, "concat": 2,
}
THIRD_TASK1_AUTO_TOTAL_POINTS = 30


def calculate_task1_auto_score(summary):
    score = sum(
        THIRD_TASK1_AUTO_POINTS.get(str(question.get("question", "")), 0)
        for question in summary.get("questions", [])
        if question.get("status") == "OK"
    )
    extra = next(
        (question.get("extra_points", 0) for question in summary.get("questions", [])
         if question.get("question") == "extra"),
        0,
    )
    return min(THIRD_TASK1_AUTO_TOTAL_POINTS, score + extra)


def add_task1_score_badges(html, file_summaries):
    search_start = 0
    for summary in file_summaries:
        score = calculate_task1_auto_score(summary)
        required = [q for q in summary.get("questions", []) if q.get("question") != "extra"]
        has_issues = any(q.get("status") != "OK" for q in required)
        status_label = "確認が必要" if has_issues else "全問正解"
        card_start = html.find("<div class='card-top'>", search_start)
        if card_start == -1:
            break
        card_end = html.find("</div>", card_start)
        if card_end == -1:
            break
        marker = "<span class='status-pill'>{}</span>".format(status_label)
        replacement = (
            "<div class='task1-status-row'>" + marker
            + "<span class='task1-point-score'>{}点/30点</span></div>".format(score)
        )
        card_html = html[card_start:card_end].replace(marker, replacement, 1)
        html = html[:card_start] + card_html + html[card_end:]
        search_start = card_start + len(card_html)
    return html


def add_task_title_style(html):
    extra_css = """
.period-with-week {
  display: inline-flex;
  align-items: flex-end;
  gap: 0;
  letter-spacing: -0.08em;
}

.period-main {
  display: inline-block;
}

.period-week {
  display: inline-block;
  font-size: 0.63em;
  font-weight: 950;
  line-height: 1;
  margin-bottom: 0.10em;
  letter-spacing: -0.06em;
  transform: translateX(-0.04em);
}

.task1-status-row {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.task1-status-row .status-pill,
.task1-point-score {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 950;
  letter-spacing: 0.04em;
  line-height: 1;
  white-space: nowrap;
}

.task1-point-score {
  background: rgba(11, 11, 13, 0.06);
  color: rgba(11, 11, 13, 0.78);
}
"""
    return html.replace("</style>", extra_css + "\n</style>", 1)


def build_index_html(message=""):
    import web_app

    html = web_app.build_index_html(message)
    html = html.replace("href='/period'>選択画面へ戻る</a>", "href='/period/3'>選択画面へ戻る</a>")
    html = html.replace("action='/check'", "action='/period/3/task1/check'")
    html = html.replace("Ocaml 1期", "OCaml 3期 課題1")
    html = html.replace("OCaml 1期", "OCaml 3期 課題1")
    html = html.replace(
        "OCaml<br>1期",
        'OCaml<br><span class="period-with-week"><span class="period-main">3期</span><span class="period-week">課題1</span></span>'
    )
    html = add_task_title_style(html)
    return html


def build_result_html(all_results, file_summaries):
    import web_app

    html = web_app.build_result_html(all_results, file_summaries)
    html = html.replace("Ocaml 1期", "OCaml 3期 課題1")
    html = html.replace("OCaml 1期", "OCaml 3期 課題1")
    html = add_task1_score_badges(html, file_summaries)
    html = add_task_title_style(html)
    return html
