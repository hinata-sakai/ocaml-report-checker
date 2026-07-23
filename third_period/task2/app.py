# -*- coding: utf-8 -*-

"""Upload and result pages for third-period task 2."""

import re


THIRD_TASK2_AUTO_POINTS = {
    "vempty": 2,
    "at": 2,
    "vector": 2,
    "vlength": 2,
    "vshow": 2,
    "isvempty": 2,
}
THIRD_TASK2_AUTO_TOTAL_POINTS = 24
THIRD_TASK2_REQUIRED_TOTAL_QUESTIONS = 6
TASK2_QUESTION_LABELS = list(THIRD_TASK2_AUTO_POINTS)


def calculate_task2_auto_score(summary):
    return min(
        THIRD_TASK2_AUTO_TOTAL_POINTS,
        sum(
            THIRD_TASK2_AUTO_POINTS.get(str(question.get("question", "")), 0)
            for question in summary.get("questions", [])
            if question.get("status") == "OK"
        ),
    )


def count_task2_statuses(summary):
    counts = {"OK": 0, "NG": 0, "ERROR": 0, "WARNING": 0}
    for question in summary.get("questions", []):
        status = str(question.get("status", ""))
        if status in counts:
            counts[status] += 1
    return counts


def add_task2_score_badges(html, file_summaries):
    search_start = 0
    for summary in file_summaries:
        score = calculate_task2_auto_score(summary)
        all_correct = all(
            question.get("status") == "OK"
            for question in summary.get("questions", [])
        ) and len(summary.get("questions", [])) == THIRD_TASK2_REQUIRED_TOTAL_QUESTIONS
        label = "全問正解" if all_correct else "確認が必要"
        card_start = html.find("<div class='card-top'>", search_start)
        if card_start == -1:
            break
        card_end = html.find("</div>", card_start)
        if card_end == -1:
            break
        marker = "<span class='status-pill'>{}</span>".format(label)
        replacement = (
            "<div class='task2-status-row'>{}"
            "<span class='task2-point-score'>{}点/{}点</span></div>"
        ).format(marker, score, THIRD_TASK2_AUTO_TOTAL_POINTS)
        card_html = html[card_start:card_end]
        new_card_html = card_html.replace(marker, replacement, 1)
        html = html[:card_start] + new_card_html + html[card_end:]
        search_start = card_start + len(new_card_html)
    return html


def replace_count_before_label(segment, label_pattern, count):
    labels = list(re.finditer(label_pattern, segment))
    if not labels:
        return segment
    before = segment[:labels[-1].start()]
    after = segment[labels[-1].start():]
    matches = list(re.finditer(r"(\d+)(\s*問)", before))
    if not matches:
        return segment
    match = matches[-1]
    return before[:match.start(1)] + str(count) + before[match.end(1):] + after


def fix_task2_result_display(html, file_summaries):
    search_start = 0
    for summary in file_summaries:
        counts = count_task2_statuses(summary)
        card_start = html.find("<div class='card-top'>", search_start)
        if card_start == -1:
            break
        next_card = html.find("<div class='card-top'>", card_start + 1)
        card_end = len(html) if next_card == -1 else next_card
        card = html[card_start:card_end]

        denominator = re.search(r"/\d+問", card)
        if denominator:
            before = card[:denominator.start()]
            after = card[denominator.end():]
            before = replace_count_before_label(before, r"不正解", counts["NG"])
            before = replace_count_before_label(before, r"エラー", counts["ERROR"])
            before = replace_count_before_label(before, r"警告", counts["WARNING"])
            before = replace_count_before_label(before, r"(?<!不)正解", counts["OK"])
            card = before + "/6問" + after

        percent = counts["OK"] / THIRD_TASK2_REQUIRED_TOTAL_QUESTIONS * 100
        card = re.sub(
            r"(style=['\"][^'\"]*width:\s*)[0-9.]+%",
            lambda match: match.group(1) + "{:.6f}%".format(percent),
            card,
            count=1,
        )
        html = html[:card_start] + card + html[card_end:]
        search_start = card_start + len(card)
    return html


def remove_task2_question_prefix(html):
    for label in TASK2_QUESTION_LABELS:
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
.period-main { display: inline-block; }
.period-week {
  display: inline-block;
  font-size: 0.63em;
  font-weight: 950;
  line-height: 1;
  margin-bottom: 0.10em;
  letter-spacing: -0.06em;
  transform: translateX(-0.04em);
}
.task2-status-row {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-shrink: 0;
}
.task2-status-row .status-pill,
.task2-point-score {
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
.task2-point-score {
  background: rgba(11, 11, 13, 0.06);
  color: rgba(11, 11, 13, 0.78);
}
"""
    return html.replace("</style>", extra_css + "\n</style>", 1)


def replace_title(html):
    html = html.replace("Ocaml 1期", "OCaml 3期 課題2")
    html = html.replace("OCaml 1期", "OCaml 3期 課題2")
    return html.replace(
        "OCaml<br>1期",
        '<span>OCaml</span><br><span class="period-with-week">'
        '<span class="period-main">3期</span>'
        '<span class="period-week">課題2</span></span>',
    )


def build_index_html(message=""):
    import web_app

    html = web_app.build_index_html(message)
    html = html.replace(
        "href='/period'>選択画面へ戻る</a>",
        "href='/period/3'>選択画面へ戻る</a>",
    )
    html = html.replace("action='/check'", "action='/period/3/task2/check'")
    return add_task_title_style(replace_title(html))


def build_result_html(all_results, file_summaries):
    import web_app

    html = web_app.build_result_html(all_results, file_summaries)
    html = replace_title(html)
    html = remove_task2_question_prefix(html)
    html = html.replace("/0問", "/6問")
    html = fix_task2_result_display(html, file_summaries)
    html = add_task2_score_badges(html, file_summaries)
    return add_task_title_style(html)
