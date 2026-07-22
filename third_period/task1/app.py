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
THIRD_TASK1_REQUIRED_TOTAL_QUESTIONS = 13

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


def count_task1_required_statuses(summary):
    counts = {
        "OK": 0,
        "NG": 0,
        "ERROR": 0,
        "WARNING": 0,
    }

    for question in summary.get("questions", []):
        question_id = str(question.get("question", ""))

        if question_id == "extra":
            continue

        status = str(question.get("status", ""))

        if status in counts:
            counts[status] += 1

    return counts


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


def build_task1_extra_note(summary):
    if get_task1_extra_points_from_summary(summary) > 0:
        note_text = "追加の関数があります。確認してください。"
        note_class = "task1-extra-note has-extra"
    else:
        note_text = "追加の関数はありません。"
        note_class = "task1-extra-note no-extra"

    return (
        "<div class='{}'>"
        "{}"
        "</div>"
    ).format(note_class, note_text)


def add_task1_extra_note_above_issue_area(html, file_summaries):
    labels = [
        "間違えた問",
        "エラーの出た問",
        "確認が必要な問はありません",
    ]

    search_start = 0

    for summary in file_summaries:
        note = build_task1_extra_note(summary)

        card_top_start = html.find("<div class='card-top'>", search_start)

        if card_top_start == -1:
            break

        next_card_top_start = html.find("<div class='card-top'>", card_top_start + 1)

        if next_card_top_start == -1:
            card_end = len(html)
        else:
            card_end = next_card_top_start

        insert_positions = []

        for label in labels:
            pos = html.find(label, card_top_start, card_end)

            if pos != -1:
                insert_positions.append(pos)

        if not insert_positions:
            search_start = card_end
            continue

        first_label_pos = min(insert_positions)
        tag_start = html.rfind("<", card_top_start, first_label_pos)

        if tag_start == -1:
            tag_start = first_label_pos

        html = html[:tag_start] + note + html[tag_start:]

        search_start = card_end + len(note)

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


def remove_task1_extra_from_summaries(file_summaries):
    filtered_summaries = []

    for summary in file_summaries:
        filtered_summary = dict(summary)

        filtered_questions = [
            question
            for question in summary.get("questions", [])
            if str(question.get("question", "")) != "extra"
        ]

        filtered_summary["questions"] = filtered_questions
        filtered_summaries.append(filtered_summary)

    return filtered_summaries


def is_task1_extra_result(result):
    if not isinstance(result, dict):
        return False

    question = str(result.get("question", ""))
    test = str(result.get("test", ""))
    name = str(result.get("name", ""))

    return question == "extra" or test == "extra" or name == "extra"


def remove_task1_extra_from_all_results(all_results):
    if isinstance(all_results, dict):
        if is_task1_extra_result(all_results):
            return None

        return all_results

    if isinstance(all_results, list):
        filtered = []

        for item in all_results:
            cleaned_item = remove_task1_extra_from_all_results(item)

            if cleaned_item is None:
                continue

            filtered.append(cleaned_item)

        return filtered

    return all_results


def fix_task1_question_total_display(html):
    html = html.replace("/14問", "/13問")
    html = html.replace("/0問", "/13問")
    return html


def replace_count_before_last_label(segment_html, label, new_count):
    import re

    label_matches = list(re.finditer(re.escape(label), segment_html))

    if not label_matches:
        return segment_html

    label_match = label_matches[-1]

    before_label = segment_html[:label_match.start()]
    after_label = segment_html[label_match.start():]

    count_matches = list(re.finditer(r"(\d+)(\s*問)", before_label))

    if not count_matches:
        return segment_html

    count_match = count_matches[-1]

    before_label = (
        before_label[:count_match.start(1)]
        + str(new_count)
        + before_label[count_match.end(1):]
    )

    return before_label + after_label


def fix_task1_result_count_display(html, file_summaries):
    import re

    search_start = 0

    for summary in file_summaries:
        counts = count_task1_required_statuses(summary)

        card_start = html.find("<div class='card-top'>", search_start)

        if card_start == -1:
            break

        next_card_start = html.find("<div class='card-top'>", card_start + 1)

        if next_card_start == -1:
            card_end = len(html)
        else:
            card_end = next_card_start

        card_html = html[card_start:card_end]

        denominator_match = re.search(r"/\d+問", card_html)

        if denominator_match:
            before_denominator = card_html[:denominator_match.start()]
            after_denominator = card_html[denominator_match.end():]

            before_denominator = replace_count_before_last_label(
                before_denominator,
                "正解",
                counts["OK"],
            )

            before_denominator = replace_count_before_last_label(
                before_denominator,
                "不正解",
                counts["NG"],
            )

            before_denominator = replace_count_before_last_label(
                before_denominator,
                "エラー",
                counts["ERROR"],
            )

            before_denominator = replace_count_before_last_label(
                before_denominator,
                "警告",
                counts["WARNING"],
            )

            card_html = (
                before_denominator
                + "/{}問".format(THIRD_TASK1_REQUIRED_TOTAL_QUESTIONS)
                + after_denominator
            )

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

.task1-extra-note {
  margin: 0 0 18px 0;
  color: rgba(11, 11, 13, 0.78);
  font-size: 15px;
  font-weight: 800;
  line-height: 1.7;
}

.task1-extra-note.has-extra {
  color: rgba(11, 11, 13, 0.78);
}

.task1-extra-note.no-extra {
  color: rgba(11, 11, 13, 0.78);
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

    display_all_results = remove_task1_extra_from_all_results(all_results)
    display_file_summaries = remove_task1_extra_from_summaries(file_summaries)

    html = web_app.build_result_html(display_all_results, display_file_summaries)
    html = html.replace("Ocaml 1期", "OCaml 3期 課題1")
    html = html.replace("OCaml 1期", "OCaml 3期 課題1")

    html = remove_task1_extra_from_issue_list(html)
    html = remove_task1_question_prefix(html)
    html = fix_task1_question_total_display(html)

    html = add_task1_extra_note_above_issue_area(html, file_summaries)
    html = add_task1_score_badges(html, file_summaries)
    html = fix_task1_result_count_display(html, file_summaries)
    html = add_task_title_style(html)

    return html