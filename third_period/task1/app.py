# -*- coding: utf-8 -*-

"""Upload and result pages for third-period task 1."""

THIRD_TASK1_AUTO_POINTS = {
    "create": 2,
    "unshift": 2,
    "shift": 2,
    "push": 2,
    "pop": 2,
    "size": 2,
    "max": 2,
    "min": 2,
    "get": 2,
    "indexOf": 2,
    "set": 2,
    "remove": 2,
    "concat": 2,
}

THIRD_TASK1_AUTO_TOTAL_POINTS = 26

TASK1_QUESTION_LABELS = [
    "create",
    "unshift",
    "shift",
    "push",
    "pop",
    "size",
    "max",
    "min",
    "get",
    "indexOf",
    "set",
    "remove",
    "concat",
    "extra",
]


def calculate_task1_auto_score(summary):
    score = 0

    for question in summary.get("questions", []):
        question_id = str(question.get("question", ""))

        if question_id == "extra":
            continue

        if question.get("status") == "OK":
            score += THIRD_TASK1_AUTO_POINTS.get(question_id, 0)

    return min(THIRD_TASK1_AUTO_TOTAL_POINTS, score)


def has_task1_required_issues(summary):
    for question in summary.get("questions", []):
        question_id = str(question.get("question", ""))

        if question_id == "extra":
            continue

        if question.get("status") != "OK":
            return True

    return False


def get_task1_extra_points_from_summary(summary):
    for question in summary.get("questions", []):
        if str(question.get("question", "")) == "extra":
            return question.get("extra_points", 0)

    return 0


def has_any_task1_extra_function(file_summaries):
    for summary in file_summaries:
        if get_task1_extra_points_from_summary(summary) > 0:
            return True

    return False


def add_task1_score_badges(html, file_summaries):
    search_start = 0

    for summary in file_summaries:
        score = calculate_task1_auto_score(summary)
        has_issues = has_task1_required_issues(summary)
        status_label = "確認が必要" if has_issues else "全問正解"

        card_start = html.find("<div class='card-top'>", search_start)

        if card_start == -1:
            break

        card_end = html.find("</div>", card_start)

        if card_end == -1:
            break

        marker = "<span class='status-pill'>{}</span>".format(status_label)

        replacement = (
            "<div class='task1-status-row'>"
            "{}"
            "<span class='task1-point-score'>{}点/{}点</span>"
            "</div>"
        ).format(marker, score, THIRD_TASK1_AUTO_TOTAL_POINTS)

        card_html = html[card_start:card_end]
        new_card_html = card_html.replace(marker, replacement, 1)

        html = html[:card_start] + new_card_html + html[card_end:]
        search_start = card_start + len(new_card_html)

    return html


def build_task1_extra_note(file_summaries):
    if has_any_task1_extra_function(file_summaries):
        note_text = "追加の関数があります。確認してください。"
    else:
        note_text = "追加の関数はありません。"

    return (
        "<div class='task1-extra-note'>"
        "{}"
        "</div>"
    ).format(note_text)


def add_task1_extra_note_above_issue_area(html, file_summaries):
    note = build_task1_extra_note(file_summaries)

    targets = [
        "<h3>間違えた問</h3>",
        "<h3>エラーの出た問</h3>",
        "<h3>確認が必要な問はありません</h3>",
        "<h2>間違えた問</h2>",
        "<h2>エラーの出た問</h2>",
        "<h2>確認が必要な問はありません</h2>",
        "<p class='no-issues'>確認が必要な問はありません</p>",
        "確認が必要な問はありません",
        "間違えた問",
        "エラーの出た問",
    ]

    for target in targets:
        if target in html:
            return html.replace(target, note + target, 1)

    return html


def remove_task1_extra_from_issue_list(html):
    remove_targets = [
        "<span class='question-chip'>Qextra</span>",
        "<span class='question-chip ng'>Qextra</span>",
        "<span class='question-chip error'>Qextra</span>",
        "<span class='question-chip warning'>Qextra</span>",
        "<span class='question-chip'>extra</span>",
        "<span class='question-chip ng'>extra</span>",
        "<span class='question-chip error'>extra</span>",
        "<span class='question-chip warning'>extra</span>",
    ]

    for target in remove_targets:
        html = html.replace(target, "")

    return html


def remove_task1_question_prefix(html):
    for label in TASK1_QUESTION_LABELS:
        html = html.replace("Q" + label, label)

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

.task1-extra-note {
  margin: 0 0 18px 0;
  color: rgba(11, 11, 13, 0.78);
  font-size: 15px;
  font-weight: 800;
  line-height: 1.7;
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

    html = remove_task1_extra_from_issue_list(html)
    html = remove_task1_question_prefix(html)
    html = add_task1_extra_note_above_issue_area(html, file_summaries)
    html = add_task1_score_badges(html, file_summaries)
    html = add_task_title_style(html)

    return html