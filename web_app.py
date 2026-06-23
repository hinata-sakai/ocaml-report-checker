# -*- coding: utf-8 -*-

from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import tempfile
import shutil
from email.parser import BytesParser
from email import policy
import traceback

from first_period import run_checker
import second_period_pages
from second_period.week1 import app as second_period_week1_app
from second_period.week1 import checker as second_period_week1_checker
from second_period.week2 import app as second_period_week2_app
from second_period.week2 import checker as second_period_week2_checker
from second_period.week3 import app as second_period_week3_app
from second_period.week3 import checker as second_period_week3_checker

import os

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
BACKGROUND_IMAGE = Path("webhaikei.png")
TASK17_IMAGE = Path("first_period/task17_routes.png")
WEEK2_DIFF_FORWARD_IMAGE = Path("second_period/week2/diff_forward_formula.png")
WEEK2_DIFF_CENTRAL_IMAGE = Path("second_period/week2/diff_central_formula.png")
WEEK3_ANSWER_TABLE1_IMAGE = Path("second_period/week3/week3_answer_table1.png")
WEEK3_ANSWER_TABLE2_IMAGE = Path("second_period/week3/week3_answer_table2.png")

VERSION_FILE = Path("VERSION")


def get_app_version():
    try:
        if VERSION_FILE.exists():
            version = VERSION_FILE.read_text(encoding="utf-8").strip()
            if version:
                return version
    except Exception:
        pass

    return "version unknown"


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

def get_form_text(part):
    payload = part.get_payload(decode=True)

    if payload is not None:
        charset = part.get_content_charset() or "utf-8"

        try:
            return payload.decode(charset)
        except UnicodeDecodeError:
            return payload.decode("utf-8", errors="replace")

    value = part.get_payload()

    if value is None:
        return ""

    return str(value)

FIRST_PERIOD_TOTAL_POINTS = 200


def calculate_first_period_score(summary):
    ok = summary.get("ok", 0)
    warning = summary.get("warning", 0)

    return ok * 10 + warning * 9


def add_first_period_score_badges(html, file_summaries):
    search_start = 0

    for summary in file_summaries:
        score = calculate_first_period_score(summary)

        warning_questions = [
            q for q in summary.get("questions", [])
            if q.get("status") == "WARNING"
        ]
        wrong_questions = [
            q for q in summary.get("questions", [])
            if q.get("status") == "NG"
        ]
        error_questions = [
            q for q in summary.get("questions", [])
            if q.get("status") == "ERROR"
        ]

        has_issues = bool(warning_questions or wrong_questions or error_questions)
        status_label = "確認が必要" if has_issues else "全問正解"

        card_top_start = html.find("<div class='card-top'>", search_start)
        if card_top_start == -1:
            break

        card_top_end = html.find("</div>", card_top_start)
        if card_top_end == -1:
            break

        marker = "<span class='status-pill'>{}</span>".format(status_label)

        replacement = (
            "<div class='first-period-status-row'>"
            "{}"
            "<span class='first-period-point-score'>{}点/{}点</span>"
            "</div>"
        ).format(marker, score, FIRST_PERIOD_TOTAL_POINTS)

        card_top_html = html[card_top_start:card_top_end]
        new_card_top_html = card_top_html.replace(marker, replacement, 1)

        html = (
            html[:card_top_start]
            + new_card_top_html
            + html[card_top_end:]
        )

        search_start = card_top_start + len(new_card_top_html)

    return html


def add_first_period_score_style(html):
    extra_css = """
.first-period-status-row {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.first-period-status-row .status-pill,
.first-period-point-score {
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

.first-period-point-score {
  background: rgba(11, 11, 13, 0.06);
  color: rgba(11, 11, 13, 0.78);
}
"""

    return html.replace("</style>", extra_css + "\n</style>")

def build_result_html(all_results, file_summaries):
    total_questions = sum(summary.get("total", 0) for summary in file_summaries)
    total_ok = sum(summary.get("ok", 0) for summary in file_summaries)
    overall_rate = round((total_ok / total_questions) * 100) if total_questions else 0

    def build_score_html(summary):
        ok = summary.get("ok", 0)
        warning = summary.get("warning", 0)
        ng = summary.get("ng", 0)
        error = summary.get("error", 0)
        total = summary.get("total", 0)

        pieces = []

        if ok:
            pieces.append(
                "<span class='score-piece'><span class='score-large'>{}問</span><span class='score-small ok'>正解</span></span>".format(ok)
            )

        if ng:
            pieces.append(
                "<span class='score-piece'><span class='score-large'>{}問</span><span class='score-small issue'>不正解</span></span>".format(ng)
            )

        if warning:
            pieces.append(
                "<span class='score-piece'><span class='score-large'>{}問</span><span class='score-small issue'>警告</span></span>".format(warning)
            )

        if error:
            pieces.append(
                "<span class='score-piece'><span class='score-large'>{}問</span><span class='score-small issue'>エラー</span></span>".format(error)
            )

        if not ok and not ng and not warning and not error:
            pieces.append(
                "<span class='score-piece'><span class='score-large'>0問</span><span class='score-small ok'>正解</span></span>"
            )

        pieces.append(
            "<span class='score-total'>/{}問</span>".format(total)
        )

        return "".join(pieces)

    def build_issue_detail(question_summary, status):
        question = html_escape(question_summary.get("question"))
        related_results = [
            result for result in question_summary.get("results", [])
            if result.get("status") == status
        ]

        if not related_results:
            related_results = question_summary.get("results", [])

        if status == "WARNING":
            status_label = "警告"
            reason = "実行結果は期待値と一致しましたが、実行後にOCamlの警告が出ています。"
            detail_class = "issue-detail warning-detail"
            status_class = "warning"
        elif status == "NG":
            status_label = "不正解"
            reason = "実行はできましたが、実行結果が期待値と違いました。"
            detail_class = "issue-detail wrong-detail"
            status_class = "wrong"
        else:
            status_label = "エラー"
            reason = "文法エラー・未定義関数・型エラーなどにより、採点処理まで進めませんでした。"
            detail_class = "issue-detail error-detail"
            status_class = "error"

        detail = []
        detail.append("<div class='{}'>".format(detail_class))
        detail.append(
            "<button class='issue-detail-button' type='button' data-status-label='{}' data-status-class='{}' data-question='Q{}'>Q{}</button>".format(
                html_escape(status_label),
                html_escape(status_class),
                question,
                question
            )
        )
        detail.append("<div class='issue-reason-source' hidden>")
        detail.append("<p>{}</p>".format(reason))

        if not related_results:
            detail.append("<p class='no-output'>詳細情報がありません。</p>")

        for result in related_results:
            detail.append("<div class='test-detail'>")
            detail.append("<p class='test-name'>{}</p>".format(html_escape(result.get("test"))))

            stdout = result.get("stdout", "")
            stderr = result.get("stderr", "")

            if stdout:
                detail.append("<p class='output-label'>stdout</p><pre>{}</pre>".format(html_escape(stdout)))
            if stderr:
                detail.append("<p class='output-label'>stderr</p><pre>{}</pre>".format(html_escape(stderr)))
            if not stdout and not stderr:
                detail.append("<p class='no-output'>stdout / stderr はありません。</p>")

            detail.append("</div>")

        detail.append("</div>")
        detail.append("</div>")

        return "".join(detail)

    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='ja'>")
    html.append("<head>")
    html.append("<meta charset='UTF-8'>")
    html.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append("<title>採点結果 - Ocaml 1期</title>")
    html.append("""
<style>
:root {
  --poster-mint: #86ddb1;
  --poster-mint-soft: #dff6e9;
  --poster-mint-dark: #258a59;
  --poster-ink: #0b0b0d;
  --poster-paper: #f3f3f0;
  --poster-card: rgba(255, 255, 255, 0.9);
  --poster-alert: #ff6b48;
  --poster-alert-soft: rgba(255, 107, 72, 0.14);
  --poster-warning: #d98b00;
  --poster-warning-soft: rgba(255, 184, 77, 0.20);
  --poster-error: #c62828;
  --poster-error-soft: rgba(198, 40, 40, 0.12);
}

* {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  min-height: 100%;
}

body {
  min-height: 100vh;
  overflow-x: hidden;
  background:
    linear-gradient(
      180deg,
      var(--poster-paper) 0,
      #f7f7f3 44vh,
      var(--poster-mint) 44vh,
      var(--poster-mint) 100%
    );
  color: var(--poster-ink);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.result-page {
  position: relative;
  min-height: 100vh;
  padding: 42px 24px 56px;
  overflow: hidden;
}

.result-page::before {
  content: "";
  position: absolute;
  top: -60px;
  right: -20px;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 30% 28%,
      rgba(255, 240, 165, 0.95) 0%,
      rgba(255, 227, 150, 0.78) 10%,
      rgba(255, 190, 145, 0.56) 22%,
      rgba(255, 135, 135, 0.72) 52%,
      rgba(255, 172, 120, 0.82) 100%);
  filter: blur(42px);
  opacity: 0.9;
  z-index: 0;
}

.result-shell {
  position: relative;
  z-index: 1;
  max-width: 1120px;
  margin: 0 auto;
}

.result-hero {
  display: grid;
  grid-template-columns: minmax(260px, 0.92fr) minmax(320px, 1fr);
  gap: 34px;
  align-items: end;
  margin-bottom: 34px;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  width: fit-content;
  padding: 7px 12px;
  border: 2px solid var(--poster-ink);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.04em;
}

.badge::before {
  content: "TA";
  display: grid;
  place-items: center;
  width: 30px;
  height: 20px;
  border-radius: 999px;
  background: var(--poster-ink);
  color: white;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0;
}

.result-title {
  margin: 20px 0 0;
  font-size: clamp(54px, 9vw, 112px);
  line-height: 0.92;
  letter-spacing: -0.08em;
  font-weight: 950;
}

.hero-copy {
  padding: 28px;
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.72);
  box-shadow: 0 20px 55px rgba(24, 88, 59, 0.14);
  backdrop-filter: blur(14px);
}

.kicker {
  margin: 0 0 8px;
  color: var(--poster-mint-dark);
  font-size: 13px;
  font-weight: 950;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.lead {
  margin: 0;
  color: rgba(11, 11, 13, 0.74);
  font-size: 17px;
  line-height: 1.8;
  font-weight: 650;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 28px;
}

.result-card {
  position: relative;
  overflow: hidden;
  padding: 26px;
  border-radius: 32px;
  background: var(--poster-card);
  border: 1px solid rgba(255, 255, 255, 0.76);
  box-shadow: 0 24px 60px rgba(24, 88, 59, 0.20);
  backdrop-filter: blur(16px);
}

.result-card::before {
  content: "";
  position: absolute;
  inset: 0 0 auto 0;
  height: 8px;
  background: var(--poster-mint-dark);
}

.result-card.needs-review::before {
  background: linear-gradient(90deg, var(--poster-alert), var(--poster-warning), var(--poster-error));
}

.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}

.file-name {
  margin: 0;
  font-size: 20px;
  font-weight: 950;
  word-break: break-all;
}

.file-name-with-student {
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-wrap: wrap;
}

.student-id-label {
  color: var(--poster-ink);
  font-size: 22px;
  font-weight: 950;
}

.student-file-label {
  color: rgba(11, 11, 13, 0.52);
  font-size: 20px;
  font-weight: 950;
}

.status-pill {
  flex: 0 0 auto;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(37, 138, 89, 0.12);
  color: var(--poster-mint-dark);
  font-size: 12px;
  font-weight: 950;
  letter-spacing: 0.04em;
}

.needs-review .status-pill {
  background: var(--poster-alert-soft);
  color: #c63c1c;
}

.score-line {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 16px;
}

.score-main {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 4px 12px;
}

.score-large {
  font-size: clamp(24px, 4vw, 42px);
  line-height: 1.14;
  font-weight: 950;
  letter-spacing: -0.05em;
}

.score-small {
  color: rgba(11, 11, 13, 0.58);
  font-size: 16px;
  font-weight: 900;
  margin-left: 4px;
}

.score-small.ok {
  color: var(--poster-mint-dark);
}

.score-small.issue {
  color: #c63c1c;
}

.score-total {
  color: rgba(11, 11, 13, 0.58);
  font-size: 16px;
  font-weight: 900;
}

.score-piece {
  display: inline-flex;
  align-items: baseline;
}

.progress {
  height: 12px;
  margin: 0 0 18px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(11, 11, 13, 0.08);
}

.progress-bar {
  display: block;
  height: 100%;
  width: var(--score-width);
  border-radius: inherit;
  background: linear-gradient(90deg, var(--poster-mint-dark), var(--poster-mint));
}

.needs-review .progress-bar {
  background: linear-gradient(90deg, var(--poster-alert), #ffba6a);
}

.issue-block {
  padding: 16px 18px;
  border-radius: 22px;
  background: rgba(134, 221, 177, 0.22);
  border: 1px solid rgba(37, 138, 89, 0.18);
}

.needs-review .issue-block {
  background: rgba(255, 255, 255, 0.58);
  border-color: rgba(11, 11, 13, 0.10);
}

.issue-section + .issue-section {
  margin-top: 14px;
}

.issue-title {
  margin: 0 0 10px;
  color: rgba(11, 11, 13, 0.64);
  font-size: 13px;
  font-weight: 950;
  letter-spacing: 0.04em;
}

.no-issues {
  margin: 0;
  color: var(--poster-mint-dark);
  font-size: 15px;
  font-weight: 900;
}

.issue-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.issue-detail {
  display: inline-block;
}

.issue-detail-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 46px;
  padding: 8px 10px;
  border: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  font-size: 14px;
  font-weight: 950;
  cursor: pointer;
  box-shadow: 0 8px 18px rgba(181, 55, 24, 0.12);
  transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.issue-detail-button:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 10px 22px rgba(181, 55, 24, 0.16);
}

.wrong-detail .issue-detail-button {
  color: #b83217;
}

.warning-detail .issue-detail-button {
  color: #9a6200;
  background: var(--poster-warning-soft);
}

.error-detail .issue-detail-button {
  color: var(--poster-error);
  background: var(--poster-error-soft);
}

.issue-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1300;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(11, 11, 13, 0.38);
  backdrop-filter: blur(10px);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.22s ease;
}

.issue-modal-overlay.show {
  opacity: 1;
  pointer-events: auto;
}

.issue-modal {
  width: min(720px, 100%);
  max-height: min(82vh, 720px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 28px;
  border: 2px solid var(--poster-ink);
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 28px 70px rgba(11, 11, 13, 0.28);
}

.issue-modal-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.issue-modal-status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 13px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 950;
}

.issue-modal-status.wrong {
  background: var(--poster-alert-soft);
  color: #c63c1c;
}

.issue-modal-status.warning {
  background: var(--poster-warning-soft);
  color: #9a6200;
}

.issue-modal-status.error {
  background: var(--poster-error-soft);
  color: var(--poster-error);
}

.issue-modal-question {
  font-size: 26px;
  font-weight: 950;
  letter-spacing: -0.04em;
}

.issue-modal-content {
  color: rgba(11, 11, 13, 0.76);
  max-height: calc(82vh - 170px);
  min-height: 0;
  overflow-y: auto;
  padding-right: 10px;
  scrollbar-gutter: stable;
}

.issue-modal-content > p {
  margin: 0 0 14px;
  line-height: 1.7;
  font-weight: 750;
}

.issue-modal-actions {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.issue-modal-close {
  min-width: 120px;
  border: 2px solid var(--poster-ink);
  border-radius: 999px;
  padding: 11px 18px;
  background: var(--poster-ink);
  color: white;
  font-size: 14px;
  font-weight: 950;
  cursor: pointer;
  box-shadow: 0 12px 26px rgba(11, 11, 13, 0.22);
  transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.issue-modal-close:hover {
  transform: translateY(-2px);
  background: #1f1f22;
  box-shadow: 0 16px 30px rgba(11, 11, 13, 0.26);
}

.issue-reason {
  width: min(620px, calc(100vw - 96px));
  margin-top: 10px;
  padding: 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(11, 11, 13, 0.10);
  color: rgba(11, 11, 13, 0.76);
  box-shadow: 0 16px 36px rgba(11, 11, 13, 0.12);
}

.issue-reason p {
  margin: 0 0 10px;
  line-height: 1.7;
  font-weight: 700;
}

.test-detail {
  padding-top: 10px;
  border-top: 1px solid rgba(11, 11, 13, 0.08);
}

.test-detail + .test-detail {
  margin-top: 12px;
}

.test-name,
.output-label,
.no-output {
  margin: 0 0 6px;
  color: rgba(11, 11, 13, 0.62);
  font-size: 12px;
  font-weight: 950;
}

pre {
  margin: 0 0 10px;
  max-height: 220px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  padding: 10px;
  border-radius: 12px;
  background: rgba(11, 11, 13, 0.06);
  color: rgba(11, 11, 13, 0.78);
  font-size: 12px;
}

.back-link {
  position: relative;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  width: fit-content;
  margin-bottom: 28px;
  padding: 10px 18px;
  border: 2px solid var(--poster-ink);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--poster-ink);
  text-decoration: none;
  font-size: 14px;
  font-weight: 900;
  letter-spacing: 0.02em;
  box-shadow: 0 10px 24px rgba(11, 11, 13, 0.08);
  transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.back-link::before {
  content: "";
  display: inline-block;
  width: 0;
  height: 0;
  border-top: 7px solid transparent;
  border-bottom: 7px solid transparent;
  border-right: 11px solid var(--poster-ink);
}

.back-link:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 28px rgba(11, 11, 13, 0.14);
}

.guide-menu-wrap {
  position: absolute;
  top: 42px;
  right: 24px;
  z-index: 20;
}

.guide-menu-button {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 0;
  background: transparent;
  color: var(--poster-ink);
  font-size: 32px;
  font-weight: 900;
  line-height: 1;
  cursor: pointer;
  box-shadow: none;
  backdrop-filter: none;
  transition:
    transform 0.2s ease,
    opacity 0.2s ease;
}

.guide-menu-button:hover {
  transform: translateY(-1px);
  background: transparent;
  box-shadow: none;
  opacity: 0.72;
}

.guide-menu-panel {
  position: absolute;
  top: 54px;
  right: 0;
  width: 190px;
  padding: 8px;
  border: 1px solid rgba(11, 11, 13, 0.12);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 18px 42px rgba(11, 11, 13, 0.16);
  backdrop-filter: blur(16px);
  opacity: 0;
  transform: translateY(-6px) scale(0.98);
  pointer-events: none;
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}

.guide-menu-wrap.open .guide-menu-panel {
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: auto;
}

.guide-menu-item {
  width: 100%;
  border: none;
  border-radius: 12px;
  padding: 12px 14px;
  background: transparent;
  color: rgba(11, 11, 13, 0.82);
  text-align: left;
  font-size: 14px;
  font-weight: 900;
  cursor: pointer;
  transition:
    background 0.18s ease,
    transform 0.18s ease;
}

.guide-menu-item:hover {
  background: rgba(134, 221, 177, 0.22);
  transform: translateX(2px);
}

.guide-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1400;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(11, 11, 13, 0.38);
  backdrop-filter: blur(10px);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.22s ease;
}

.guide-modal-overlay.show {
  opacity: 1;
  pointer-events: auto;
}

.guide-modal {
  width: min(760px, 100%);
  max-height: min(82vh, 760px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 28px;
  border: 2px solid var(--poster-ink);
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 28px 70px rgba(11, 11, 13, 0.28);
}

.guide-modal-title {
  margin: 0 0 16px;
  color: var(--poster-ink);
  font-size: 28px;
  font-weight: 950;
  letter-spacing: -0.04em;
}

.guide-modal-content {
  min-height: 0;
  overflow-y: auto;
  padding-right: 8px;
  color: rgba(11, 11, 13, 0.76);
}

.guide-list {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.guide-card {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(134, 221, 177, 0.16);
  border: 1px solid rgba(37, 138, 89, 0.14);
}

.guide-card-title {
  margin: 0 0 6px;
  color: var(--poster-ink);
  font-size: 15px;
  font-weight: 950;
}

.guide-card-text {
  margin: 0;
  line-height: 1.7;
  font-size: 14px;
  font-weight: 700;
}

.guide-subitems {
  margin-top: 14px;
}

.guide-subitem {
  padding-top: 14px;
}

.guide-subitem + .guide-subitem {
  margin-top: 14px;
  border-top: 1px solid rgba(37, 138, 89, 0.16);
}

.guide-intro {
  margin: 0 0 16px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(134, 221, 177, 0.14);
  border: 1px solid rgba(37, 138, 89, 0.14);
  color: rgba(11, 11, 13, 0.78);
  line-height: 1.8;
  font-size: 14px;
  font-weight: 750;
}

.guide-section-title {
  margin: 18px 0 10px;
  color: var(--poster-ink);
  font-size: 16px;
  font-weight: 950;
}

.guide-card-code {
  margin: 8px 0 0;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(11, 11, 13, 0.06);
  color: rgba(11, 11, 13, 0.76);
  font-family: Consolas, "Courier New", monospace;
  font-size: 12px;
  line-height: 1.7;
  white-space: pre-wrap;
  overflow-x: auto;
  text-align: left;
}

.guide-image-wrap {
  margin: 12px 0;
  padding: 12px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(11, 11, 13, 0.10);
}

.guide-image {
  display: block;
  width: min(100%, 460px);
  height: auto;
  margin: 0 auto;
  border-radius: 12px;
}

.guide-submit-list {
  margin: 8px 0 0;
  padding-left: 1.2em;
  line-height: 1.8;
  font-size: 14px;
  font-weight: 700;
}

.guide-status-grid {
  display: grid;
  gap: 12px;
}

.guide-status-card {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid rgba(11, 11, 13, 0.10);
}

.guide-status-label {
  display: inline-flex;
  margin-bottom: 8px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 950;
}

.guide-status-label.ok {
  background: rgba(37, 138, 89, 0.12);
  color: var(--poster-mint-dark);
}

.guide-status-label.ng {
  background: rgba(255, 107, 72, 0.14);
  color: #c63c1c;
}

.guide-status-label.warning {
  background: rgba(255, 184, 77, 0.20);
  color: #9a6200;
}

.guide-status-label.error {
  background: rgba(198, 40, 40, 0.12);
  color: var(--poster-error);
}

.guide-modal-actions {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.guide-modal-close {
  min-width: 120px;
  border: 2px solid var(--poster-ink);
  border-radius: 999px;
  padding: 11px 18px;
  background: var(--poster-ink);
  color: white;
  font-size: 14px;
  font-weight: 950;
  cursor: pointer;
  box-shadow: 0 12px 26px rgba(11, 11, 13, 0.22);
  transition:
    transform 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease;
}

.guide-modal-close:hover {
  transform: translateY(-2px);
  background: #1f1f22;
  box-shadow: 0 16px 30px rgba(11, 11, 13, 0.26);
}

@media (max-width: 780px) {
  .result-page {
    padding: 28px 18px 44px;
  }

  .result-page::before {
    width: 180px;
    height: 180px;
    right: -42px;
    top: 42px;
  }

  .result-hero {
    grid-template-columns: 1fr;
  }

  .result-grid {
    grid-template-columns: 1fr;
  }

  .hero-copy {
    padding: 22px;
  }

  .card-top,
  .score-line {
    align-items: flex-start;
    flex-direction: column;
  }

  .issue-reason {
    width: calc(100vw - 72px);
  }
}
</style>
""")
    html.append("</head>")
    html.append("<body>")
    html.append("<main class='result-page'>")
    html.append("<a class='back-link' href='/upload' id='back-to-upload-link'>ファイル選択へ戻る</a>")
    html.append("<div class='guide-menu-wrap' id='guide-menu-wrap'>")
    html.append("<button class='guide-menu-button' id='guide-menu-button' type='button' aria-label='課題一覧と採点基準を開く'>☰</button>")
    html.append("<div class='guide-menu-panel' id='guide-menu-panel'>")
    html.append("<button class='guide-menu-item' type='button' data-guide='tasks'>課題内容</button>")
    html.append("<button class='guide-menu-item' type='button' data-guide='criteria'>採点基準</button>")
    html.append("</div>")
    html.append("</div>")
    html.append("<div class='result-shell'>")
    html.append("<section class='result-hero'>")
    html.append("<div>")
    html.append("<div class='badge'>Report Checker</div>")
    html.append("<h1 class='result-title'>採点<br>結果</h1>")
    html.append("</div>")
    html.append("<div class='hero-copy'>")
    html.append("<p class='kicker'>Ocaml 1期 / Result</p>")
    html.append("<p class='lead'>採点結果と確認が必要な問を、ファイルごとにまとめて表示しています。</p>")
    html.append("</div>")
    html.append("</section>")

    html.append("<section class='result-grid' aria-label='ファイルごとの採点結果'>")
    for summary in file_summaries:
        filename = html_escape(summary["file"])
        student_id = html_escape(summary.get("student_id", ""))
        ok = summary.get("ok", 0)
        total = summary.get("total", 0)
        warning_questions = [q for q in summary.get("questions", []) if q.get("status") == "WARNING"]
        wrong_questions = [q for q in summary.get("questions", []) if q.get("status") == "NG"]
        error_questions = [q for q in summary.get("questions", []) if q.get("status") == "ERROR"]
        has_issues = bool(warning_questions or wrong_questions or error_questions)
        score_rate = round((ok / total) * 100) if total else 0
        card_class = "result-card needs-review" if has_issues else "result-card"
        status_label = "確認が必要" if has_issues else "全問正解"

        html.append("<article class='{}'>".format(card_class))
        html.append("<div class='card-top'>")
        if student_id:
            html.append(
                "<h2 class='file-name file-name-with-student'>"
                "<span class='student-id-label'>{}</span>"
                "<span class='student-file-label'>{}</span>"
                "</h2>".format(student_id, filename)
            )
        else:
            html.append("<h2 class='file-name'>{}</h2>".format(filename))
        html.append("<span class='status-pill'>{}</span>".format(status_label))
        html.append("</div>")
        html.append("<div class='score-line'>")
        html.append("<span class='score-main'>{}</span>".format(build_score_html(summary)))
        html.append("</div>")
        html.append("<div class='progress' aria-label='正答率 {}%'>".format(score_rate))
        html.append("<span class='progress-bar' style='--score-width: {}%;'></span>".format(score_rate))
        html.append("</div>")
        html.append("<div class='issue-block'>")

        if wrong_questions:
            html.append("<div class='issue-section'>")
            html.append("<p class='issue-title'>間違えた問</p>")
            html.append("<div class='issue-tags'>")
            for question_summary in wrong_questions:
                html.append(build_issue_detail(question_summary, "NG"))
            html.append("</div>")
            html.append("</div>")

        if warning_questions:
            html.append("<div class='issue-section'>")
            html.append("<p class='issue-title'>警告の出た問</p>")
            html.append("<div class='issue-tags'>")
            for question_summary in warning_questions:
                html.append(build_issue_detail(question_summary, "WARNING"))
            html.append("</div>")
            html.append("</div>")

        if error_questions:
            html.append("<div class='issue-section'>")
            html.append("<p class='issue-title'>エラーの出た問</p>")
            html.append("<div class='issue-tags'>")
            for question_summary in error_questions:
                html.append(build_issue_detail(question_summary, "ERROR"))
            html.append("</div>")
            html.append("</div>")

        if not has_issues:
            html.append("<p class='no-issues'>確認が必要な問はありません</p>")

        html.append("</div>")
        html.append("</article>")

    html.append("</section>")
    html.append("</div>")
    html.append("</main>")

    html.append("<div class='guide-modal-overlay' id='guide-modal-overlay' aria-hidden='true'>")
    html.append("<div class='guide-modal' role='dialog' aria-modal='true' aria-labelledby='guide-modal-title'>")
    html.append("<h2 class='guide-modal-title' id='guide-modal-title'></h2>")
    html.append("<div class='guide-modal-content' id='guide-modal-content'></div>")
    html.append("<div class='guide-modal-actions'>")
    html.append("<button class='guide-modal-close' type='button' id='guide-modal-close'>閉じる</button>")
    html.append("</div>")
    html.append("</div>")
    html.append("</div>")

    html.append("<div class='issue-modal-overlay' id='issue-modal-overlay' aria-hidden='true'>")
    html.append("<div class='issue-modal' role='dialog' aria-modal='true' aria-labelledby='issue-modal-question'>")
    html.append("<div class='issue-modal-header'>")
    html.append("<span class='issue-modal-status' id='issue-modal-status'></span>")
    html.append("<span class='issue-modal-question' id='issue-modal-question'></span>")
    html.append("</div>")
    html.append("<div class='issue-modal-content' id='issue-modal-content'></div>")
    html.append("<div class='issue-modal-actions'>")
    html.append("<button class='issue-modal-close' type='button' id='issue-modal-close'>閉じる</button>")
    html.append("</div>")
    html.append("</div>")
    html.append("</div>")

    html.append("""
<script>
document.addEventListener('DOMContentLoaded', function () {
  const backToUploadLink = document.getElementById('back-to-upload-link');

  if (backToUploadLink) {
    backToUploadLink.addEventListener('click', function (e) {
      e.preventDefault();

      if (window.parent && window.parent !== window) {
        window.parent.postMessage({ type: 'close-result-frame' }, '*');
        return;
      }

      if (window.history.length > 1) {
        window.history.back();
      } else {
        window.location.href = '/upload';
      }
    });
  }

  const guideMenuWrap = document.getElementById('guide-menu-wrap');
  const guideMenuButton = document.getElementById('guide-menu-button');
  const guideModalOverlay = document.getElementById('guide-modal-overlay');
  const guideModalTitle = document.getElementById('guide-modal-title');
  const guideModalContent = document.getElementById('guide-modal-content');
  const guideModalClose = document.getElementById('guide-modal-close');

  const taskGuideHtml = `
    <p class="guide-intro">
      下記の1から16までは，実行すると記述してあるような結果になる関数がある。
      この結果になるときどのような動作をするか考えて，それらを日本語で説明しなさい。
      また，17についても実行例についてどのように動作しているのか，日本語で説明しなさい。
      18から20は説明に対する動作例を自分で考え，そのときの動作を日本語で説明しなさい。
      また，各問いに対するOCaml定義を行い，ソースコードを作成しなさい。
      すべてのソースコードは一つのファイルにまとめること。
    </p>

    <h3 class="guide-section-title">1〜16. 実行例から動作を説明する関数</h3>

    <ul class="guide-list">
      <li class="guide-card">
        <p class="guide-card-title">1. checkl</p>
        <p class="guide-card-text">指定した値がリストの中に含まれているかを判定する関数。</p>
        <pre class="guide-card-code"># checkl;;
  - : 'a -> 'a list -> bool = &lt;fun&gt;
  # checkl 3 [1; 2; 3; 4; 5; 6];;
  - : bool = true
  # checkl 1 [2; 3; 4; 5];;
  - : bool = false</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">2. dellt</p>
        <p class="guide-card-text">指定した位置以降のリストを返す関数。負の値の場合は例外を発生させる。</p>
        <pre class="guide-card-code"># dellt;;
  - : int -> 'a list -> 'a list = &lt;fun&gt;
  # dellt 0 [1;2;3;4];;
  - : int list = [1; 2; 3; 4]
  # dellt 1 [1;2;3;4];;
  - : int list = [2; 3; 4]
  # dellt 2 [1;2;3;4];;
  - : int list = [3; 4]
  # dellt 3 [1;2;3;4];;
  - : int list = [4]
  # dellt 5 [1;2;3;4];;
  - : int list = []
  # dellt 3 ["A"; "B"; "C"; "D"; "E"; "F"];;
  - : string list = ["D"; "E"; "F"]
  # dellt(-2) [1; 2];;
  Exception: Failure "Error".</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">3. dellt2</p>
        <p class="guide-card-text">指定した位置の要素だけをリストから取り除く関数。</p>
        <pre class="guide-card-code"># dellt2;;
  - : int -> 'a list -> 'a list = &lt;fun&gt;
  # dellt2 1 ["A"; "B"; "C"; "D"; "E"; "F"];;
  - : string list = ["B"; "C"; "D"; "E"; "F"]
  # dellt2 3 ["A"; "B"; "C"; "D"; "E"; "F"];;
  - : string list = ["A"; "B"; "D"; "E"; "F"]
  # dellt2 3 [1; 2; 3; 4; 5; 6];;
  - : int list = [1; 2; 4; 5; 6]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">4. posl</p>
        <p class="guide-card-text">指定した位置の要素を取り出す関数。存在しない位置の場合は例外を発生させる。</p>
        <pre class="guide-card-code"># posl;;
  - : int -> 'a list -> 'a = &lt;fun&gt;
  # posl 3 ["AB"; "C"; "DEF"; "G"; "H"; "IJ"];;
  - : string = "DEF"
  # posl 2 [ 1; 2; 3; 4; 5];;
  - : int = 2
  # posl 0 [ 1; 2; 3; 4; 5];;
  Exception: Failure "Not Exist...".</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">5. add2list</p>
        <p class="guide-card-text">隣り合う要素同士を足し合わせた結果をリストとして返す関数。</p>
        <pre class="guide-card-code"># add2list;;
  - : int list -> int list = &lt;fun&gt;
  # add2list [1; 2];;
  - : int list = [3]
  # add2list [1; 2; 3];;
  - : int list = [3; 5]
  # add2list [1; 2; 3; 4; 5];;
  - : int list = [3; 5; 7; 9]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">6. mullist</p>
        <p class="guide-card-text">2つのリストの同じ位置にある要素同士を掛け合わせたリストを返す関数。</p>
        <pre class="guide-card-code"># mullist;;
  - : int list -> int list -> int list = &lt;fun&gt;
  # mullist [1; 3; 5; 7] [2; 4; 6; 8];;
  - : int list = [2; 12; 30; 56]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">7. chglist</p>
        <p class="guide-card-text">リスト内の指定した値を，別の値に置き換える関数。</p>
        <pre class="guide-card-code"># chglist;;
  - : 'a * 'a -> 'a list -> 'a list = &lt;fun&gt;
  # chglist ("A", "*") ["1"; "A"; "2"; "B"; "A"; "A"; "3"; "4"];;
  - : string list = ["1"; "*"; "2"; "B"; "*"; "*"; "3"; "4"]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">8. replicate</p>
        <p class="guide-card-text">指定した値を指定回数だけ繰り返したリストを作る関数。</p>
        <pre class="guide-card-code"># replicate;;
  - : int -> 'a -> 'a list = &lt;fun&gt;
  # replicate 3 ["A"];;
  - : string list list = [["A"]; ["A"]; ["A"]]
  # replicate 5 "A";;
  - : string list = ["A"; "A"; "A"; "A"; "A"]
  # replicate 3 ["1"; "#"];;
  - : string list list = [["1"; "#"]; ["1"; "#"]; ["1"; "#"]]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">9. inslist</p>
        <p class="guide-card-text">指定した位置に要素を挿入する関数。位置が0の場合は例外を発生させる。</p>
        <pre class="guide-card-code"># inslist;;
  - : int -> 'a -> 'a list -> 'a list = &lt;fun&gt;
  # inslist 2 "*" ["A"; "B"; "C"; "D"; "E"];;
  - : string list = ["A"; "*"; "B"; "C"; "D"; "E"]
  # inslist 6 "*" ["A"; "B"; "C"; "D"; "E"];;
  - : string list = ["A"; "B"; "C"; "D"; "E"; "*"]
  # inslist 1 "+" [];;
  - : string list = ["+"]
  # inslist 1 "+" ["A"];;
  - : string list = ["+"; "A"]
  # inslist 0 "+" ["A"];;
  Exception: Failure "Error".</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">10. merge</p>
        <p class="guide-card-text">2つのリストの要素を交互に並べたリストを返す関数。</p>
        <pre class="guide-card-code"># merge;;
  - : 'a list -> 'a list -> 'a list = &lt;fun&gt;
  # merge [1; 2; 3] [4; 5; 6];;
  - : int list = [1; 4; 2; 5; 3; 6]
  # merge ["A"; "B"] [ "C"; "D"; "EF"; "GH"];;
  - : string list = ["A"; "C"; "B"; "D"; "EF"; "GH"]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">11. inside_length</p>
        <p class="guide-card-text">リストの中にある各リストの要素数を合計して返す関数。</p>
        <pre class="guide-card-code"># inside_length;;
  - : 'a list list -> int = &lt;fun&gt;
  # inside_length[[1; 2; 3]; [4; 5]; [6]; [7; 8; 9; 10]];;
  - : int = 10
  # inside_length[["A"; "B"]; [ "C"; "D"]; ["EF"; "GH"]];;
  - : int = 6</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">12. concat</p>
        <p class="guide-card-text">リストの中にある複数のリストを，1つのリストにつなげる関数。</p>
        <pre class="guide-card-code"># concat;;
  - : 'a list list -> 'a list = &lt;fun&gt;
  # concat [[0; 3; 4]; [2]; [0]; [5; 0]];;
  - : int list = [0; 3; 4; 2; 0; 5; 0]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">13. assoc</p>
        <p class="guide-card-text">ペアのリストから，指定した値と対応する値を探して返す関数。</p>
        <pre class="guide-card-code"># assoc;;
  - : 'a -> ('a * 'a) list -> 'a = &lt;fun&gt;
  # assoc 33 [(3,4); (33,5); (11,2); (55,1)];;
  - : int = 5
  # assoc 2 [(3,4); (33,5); (11,2); (55,1)];;
  - : int = 11
  # assoc "03" [("Kyoto", "075"); ("Osaka", "06"); ("Tokyo", "03")];;
  - : string = "Tokyo"
  # assoc "Kyoto" [("Kyoto", "075"); ("Osaka", "06"); ("Tokyo", "03")];;
  - : string = "075"
  # assoc 6 [(3,4); (33,5); (11,2); (55,1)];;
  Exception: Failure "Not found...".</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">14. minimum</p>
        <p class="guide-card-text">リストの中で最小の要素を返す関数。空リストの場合は例外を発生させる。</p>
        <pre class="guide-card-code"># minimum;;
  - : 'a list -> 'a = &lt;fun&gt;
  # minimum [3; 2; 5; 1];;
  - : int = 1
  # minimum ["abc"; "sdf"];;
  - : string = "abc"
  # minimum [];;
  Exception: Failure "Error".</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">15. extract</p>
        <p class="guide-card-text">条件を満たす要素だけを取り出したリストを返す関数。</p>
        <pre class="guide-card-code"># extract;;
  - : ('a -> bool) -> 'a list -> 'a list = &lt;fun&gt;
  # extract (fun x -> x > 10) [21; 2; 31; 1];;
  - : int list = [21; 31]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">16. index</p>
        <p class="guide-card-text">指定した要素がリストの何番目にあるかを返す関数。先頭は0番目として数える。</p>
        <pre class="guide-card-code"># index;;
  - : 'a list -> 'a -> int = &lt;fun&gt;
  # index [21; 2; 31; 1] 21;;
  - : int = 0
  # index ['a'; '3'; 'b'; 'z'; '1'] 'z';;
  - : int = 3</pre>
      </li>
    </ul>

    <h3 class="guide-section-title">17. 経路数 numOfRotes</h3>

    <div class="guide-card">
      <p class="guide-card-title">17. 経路数: numOfRotes</p>
      <p class="guide-card-text">
        碁盤目状の道路がある。始点から終点までの経路の数を求める。
        ただし，始点から終点までの経路は最短経路のみとする。
        すなわち，進行方向は右方向または上方向に限られ，左方向または下方向に進むことはできない。
      </p>
      <div class="guide-image-wrap">
        <img class="guide-image" src="/task17_routes.png" alt="numOfRotes の経路図">
      </div>
      <pre class="guide-card-code"># numOfRotes;;
  - : int * int -> int = &lt;fun&gt;
  # numOfRotes (5, 4);;
  - : int = 126</pre>
    </div>

    <h3 class="guide-section-title">18〜20. 集合の計算</h3>

    <div class="guide-card">
      <p class="guide-card-title">集合の計算</p>
      <p class="guide-card-text">
        リストを集合と見なして，以下の集合計算をする関数を定義する。
        ただし，各集合では同じ要素の重複は許されない。
      </p>

      <div class="guide-subitems">
        <div class="guide-subitem">
          <p class="guide-card-title">18. inter</p>
          <p class="guide-card-text">二つの集合の積，共通要素を返す関数。</p>
        </div>

        <div class="guide-subitem">
          <p class="guide-card-title">19. union</p>
          <p class="guide-card-text">二つの集合の和を返す関数。</p>
        </div>

        <div class="guide-subitem">
          <p class="guide-card-title">20. diff</p>
          <p class="guide-card-text">二つの集合の差を返す関数。</p>
        </div>
      </div>
    </div>

    <h3 class="guide-section-title">課題提出</h3>

    <div class="guide-card">
      <p class="guide-card-title">提出方法</p>
      <ul class="guide-submit-list">
        <li>提出期限: 2026/5/13（水）13:00</li>
        <li>提出方法: LETUSにて提出</li>
        <li>提出物: レポート（LaTeXで作成したPDF）と，プログラムソースコード（拡張子ml）</li>
        <li>PDFおよびmlファイルは，それぞれ一つのファイルにまとめること</li>
        <li>実行例と同じ結果が出る関数を定義する</li>
        <li>18，19，20は自分で実行例を作成する</li>
        <li>実行例が表示される関数呼び出しもソースコード内に含めること</li>
        <li>Exceptionが出る呼び出しは，プログラムの動作が止まってしまうのでコメントアウトしておくこと</li>
        <li>今回の課題は考察不要</li>
      </ul>
    </div>
  `;

  const criteriaGuideHtml = `
    <div class="guide-card">
      <p class="guide-card-title">採点の基本方針</p>
      <p class="guide-card-text">
        基本的には，プログラムだけで点数をつけてください。
        課題ページと同じ動作をすれば満点です。
      </p>

      <div class="guide-subitems">
        <div class="guide-subitem">
          <p class="guide-card-title">点数配分</p>
          <ul class="guide-submit-list">
            <li>各問題10点</li>
            <li>合計200点満点</li>
          </ul>
        </div>

        <div class="guide-subitem">
          <p class="guide-card-title">採点基準</p>
          <ul class="guide-submit-list">
            <li>課題ページに書かれている動作をするプログラムの場合：10点</li>
            <li>警告が出る：9点</li>
            <li>プログラムが課題どおり動かない場合：動作の説明が適切な場合：5点</li>
          </ul>
        </div>
      </div>
    </div>
  `;

  function openGuideMenu() {
    if (!guideMenuWrap) {
      return;
    }

    guideMenuWrap.classList.toggle('open');
  }

  function closeGuideMenu() {
    if (!guideMenuWrap) {
      return;
    }

    guideMenuWrap.classList.remove('open');
  }

  function openGuideModal(type) {
    if (!guideModalOverlay || !guideModalTitle || !guideModalContent) {
      return;
    }

    if (type === 'tasks') {
      guideModalTitle.textContent = '課題内容';
      guideModalContent.innerHTML = taskGuideHtml;
    } else {
      guideModalTitle.textContent = '採点基準';
      guideModalContent.innerHTML = criteriaGuideHtml;
    }

    guideModalContent.querySelectorAll('.guide-card-code').forEach(function (codeBlock) {
      codeBlock.textContent = codeBlock.textContent
        .split('\\n')
        .map(function (line) {
          return line.replace(/^\\s+/, '');
        })
        .join('\\n')
        .trim();
    });

    closeGuideMenu();
    guideModalOverlay.classList.add('show');
    guideModalOverlay.setAttribute('aria-hidden', 'false');
  }

  function closeGuideModal() {
    if (!guideModalOverlay || !guideModalTitle || !guideModalContent) {
      return;
    }

    guideModalOverlay.classList.remove('show');
    guideModalOverlay.setAttribute('aria-hidden', 'true');

    setTimeout(function () {
      if (!guideModalOverlay.classList.contains('show')) {
        guideModalTitle.textContent = '';
        guideModalContent.innerHTML = '';
      }
    }, 220);
  }

  if (guideMenuButton) {
    guideMenuButton.addEventListener('click', function (e) {
      e.stopPropagation();
      openGuideMenu();
    });
  }

  document.querySelectorAll('.guide-menu-item').forEach(function (button) {
    button.addEventListener('click', function () {
      openGuideModal(button.getAttribute('data-guide'));
    });
  });

  if (guideModalClose) {
    guideModalClose.addEventListener('click', closeGuideModal);
  }

  if (guideModalOverlay) {
    guideModalOverlay.addEventListener('click', function (e) {
      if (e.target === guideModalOverlay) {
        closeGuideModal();
      }
    });
  }

  document.addEventListener('click', function (e) {
    if (guideMenuWrap && !guideMenuWrap.contains(e.target)) {
      closeGuideMenu();
    }
  });

  const issueModalOverlay = document.getElementById('issue-modal-overlay');
  const issueModalStatus = document.getElementById('issue-modal-status');
  const issueModalQuestion = document.getElementById('issue-modal-question');
  const issueModalContent = document.getElementById('issue-modal-content');
  const issueModalClose = document.getElementById('issue-modal-close');

  function closeIssueModal() {
    issueModalOverlay.classList.remove('show');
    issueModalOverlay.setAttribute('aria-hidden', 'true');
    issueModalStatus.textContent = '';
    issueModalStatus.className = 'issue-modal-status';
    issueModalQuestion.textContent = '';
    issueModalContent.innerHTML = '';
  }

  document.querySelectorAll('.issue-detail-button').forEach(function (button) {
    button.addEventListener('click', function () {
      const source = button.parentElement.querySelector('.issue-reason-source');
      const statusLabel = button.getAttribute('data-status-label') || '確認';
      const statusClass = button.getAttribute('data-status-class') || '';
      const question = button.getAttribute('data-question') || '';

      issueModalStatus.textContent = statusLabel;
      issueModalStatus.className = 'issue-modal-status ' + statusClass;
      issueModalQuestion.textContent = question;
      issueModalContent.innerHTML = source ? source.innerHTML : '<p>詳細情報がありません。</p>';

      issueModalOverlay.classList.add('show');
      issueModalOverlay.setAttribute('aria-hidden', 'false');
    });
  });

  issueModalClose.addEventListener('click', closeIssueModal);

  issueModalOverlay.addEventListener('click', function (e) {
    if (e.target === issueModalOverlay) {
      closeIssueModal();
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') {
      return;
    }

    closeGuideMenu();

    if (guideModalOverlay && guideModalOverlay.classList.contains('show')) {
      closeGuideModal();
    }

    if (issueModalOverlay.classList.contains('show')) {
      closeIssueModal();
    }
  });
});
</script>
""")

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
  min-height: 100%;
  overflow-x: hidden;
  overflow-y: auto;
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

.version-badge {
  position: fixed;
  top: 28px;
  right: 32px;
  z-index: 5;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 0;
  border: none;
  border-radius: 0;
  background: transparent;
  color: #ffffff;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-shadow: 0 2px 8px rgba(0,0,0,0.65);
  box-shadow: none;
  backdrop-filter: none;
}

.version-badge::before {
  content: "VERSION";
  color: #ffffff;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-shadow: 0 2px 8px rgba(0,0,0,0.65);
}

@media (max-width: 700px) {
  .version-badge {
    top: 18px;
    right: 18px;
    padding: 0;
    font-size: 14px;
  }

  .version-badge::before {
    font-size: 14px;
  }
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

@keyframes startButtonLaunch {
  0% {
    transform: scale(1);
    box-shadow: 0 4px 14px rgba(0,0,0,0.35);
  }
  45% {
    transform: scale(1.20);
    box-shadow: 0 0 34px rgba(170, 210, 255, 0.75), 0 12px 34px rgba(0,0,0,0.58);
  }
  100% {
    transform: scale(1.14);
    box-shadow: 0 0 26px rgba(120, 190, 255, 0.65), 0 10px 30px rgba(0,0,0,0.55);
  }
}

.start-button.launch {
  animation: startButtonLaunch 0.45s ease forwards;
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
    html.append("<div class='version-badge'>{}</div>".format(html_escape(get_app_version().lstrip("vV"))))

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
    html.append("<a class='start-button' id='start-button' href='/term'>採点をはじめる</a>")
    html.append("</div>")
    html.append("</div>")

    html.append("""
<script>
document.addEventListener('DOMContentLoaded', function () {
  const startButton = document.getElementById('start-button');

  startButton.addEventListener('click', function (e) {
    e.preventDefault();

    const href = startButton.getAttribute('href');

    startButton.classList.remove('launch');
    void startButton.offsetWidth;
    startButton.classList.add('launch');

    setTimeout(function () {
      window.location.href = href;
    }, 450);
  });
});
</script>
""")

    html.append("</body>")
    html.append("</html>")

    return "\n".join(html)


def build_term_select_html():
    items = [
        {"label": "前期\nOCaml演習", "href": "/period"},
        {"label": "後期\nJava演習", "href": "#", "coming_soon": True},
    ]
    return build_carousel_select_html("前期・後期選択", items, initial_index=0, back_href="/")


def build_period_select_html():
    items = [
        {"label": "1期\nOCaml演習", "href": "/upload"},
        {"label": "2期\nOCaml演習", "href": "/period/2"},
        {"label": "3期\nOCaml演習", "href": "#", "coming_soon": True},
        {"label": "4期\nOCaml演習", "href": "#", "coming_soon": True},
    ]
    return build_carousel_select_html("期選択", items, initial_index=0, back_href="/term")


def build_carousel_select_html(page_title, items, initial_index=0, back_href="/"):
    card_html_list = []
    dot_html_list = []

    for i, item in enumerate(items):
        label_lines = item["label"].split("\n")
        label_html = "<br>".join(html_escape(line) for line in label_lines)

        if item.get("coming_soon"):
            card_html_list.append(
                "<button class='carousel-card coming-soon-card' type='button' data-index='{index}' data-label='{data_label}'>{label}</button>".format(
                    index=i,
                    data_label=html_escape(item["label"].replace("\n", " ")),
                    label=label_html
                )
            )
        else:
            card_html_list.append(
                "<a class='carousel-card' href='{href}' data-index='{index}'>{label}</a>".format(
                    href=html_escape(item["href"]),
                    index=i,
                    label=label_html
                )
            )

        dot_html_list.append(
            "<button class='dot' type='button' data-index='{index}' aria-label='{label}'></button>".format(
                index=i,
                label=html_escape(item["label"].replace("\n", " "))
            )
        )

    cards_html = "\n".join(card_html_list)
    dots_html = "\n".join(dot_html_list)

    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='ja'>")
    html.append("<head>")
    html.append("<meta charset='UTF-8'>")
    html.append("<title>{}</title>".format(html_escape(page_title)))
    html.append("""
<style>
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  min-height: 100%;
  overflow-x: hidden;
  overflow-y: auto;
}

body {
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: white;
  background: #020817;
}

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

.dark-overlay {
  position: fixed;
  inset: 0;
  background:
    radial-gradient(circle at center, rgba(0, 0, 0, 0.10), rgba(0, 0, 0, 0.45)),
    linear-gradient(rgba(0, 0, 0, 0.22), rgba(0, 0, 0, 0.35));
  z-index: 1;
}

.page-fade-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0);
  opacity: 0;
  pointer-events: none;
  transition: background 1.0s ease, opacity 1.0s ease;
}

.page-fade-overlay.show {
  background: rgba(0, 0, 0, 1);
  opacity: 1;
  pointer-events: auto;
}

.page {
  position: relative;
  z-index: 4;
  min-height: 100vh;
  text-align: center;
  padding-bottom: 28px;
  box-sizing: border-box;
}

.back-button {
  position: absolute;
  top: 55%;
  right: 20%;
  z-index: 10;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.85);
  background: rgba(255, 255, 255, 0.16);
  color: rgba(255, 255, 255, 0.95);
  text-decoration: none;
  font-size: 30px;
  font-weight: 900;
  line-height: 36px;
  text-align: center;
  box-shadow: 0 0 12px rgba(255,255,255,0.22);
  transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.back-button:hover {
  transform: scale(1.08);
  background: rgba(255, 255, 255, 0.26);
  box-shadow: 0 0 18px rgba(255,255,255,0.35);
}

.header {
  padding-top: 70px;
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
  margin-bottom: 70px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.65);
}

.carousel-shell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 28px;
  width: 100%;
  margin-top: 8px;
}

.nav-btn {
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.78);
  font-size: 72px;
  font-weight: bold;
  line-height: 1;
  cursor: pointer;
  padding: 0 8px;
  z-index: 5;
  transition: transform 0.2s ease, opacity 0.2s ease, color 0.2s ease;
  text-shadow: 0 0 10px rgba(255,255,255,0.25);
}

.nav-btn:hover {
  transform: scale(1.08);
  color: rgba(255, 255, 255, 1);
}

.nav-btn:disabled {
  opacity: 0.35;
  cursor: default;
  transform: none;
}

.carousel-viewport {
  width: min(920px, 78vw);
  overflow: visible;
  position: relative;
  padding: 52px 0 52px;
  clip-path: inset(-80px 0 -80px 0);
}

.carousel-track {
  display: flex;
  align-items: center;
  gap: 54px;
  will-change: transform;
  transition: transform 0.42s ease;
}

.carousel-card {
  flex: 0 0 240px;
  height: 210px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 0 16px;
  box-sizing: border-box;
  background: #31148f;
  color: white;
  text-decoration: none;
  font-size: 28px;
  font-weight: 900;
  line-height: 1.55;
  box-shadow: 0 5px 18px rgba(0,0,0,0.4);
  transform: scale(0.82);
  opacity: 0.62;
  transition:
    transform 0.35s ease,
    opacity 0.35s ease,
    box-shadow 0.35s ease,
    background 0.35s ease;
}

.carousel-card.coming-soon-card {
  border: none;
  cursor: pointer;
  font-family: inherit;
}

.comms-panel {
  position: fixed;
  right: 32px;
  bottom: 32px;
  z-index: 30;
  width: min(360px, calc(100vw - 48px));
  padding: 18px 20px;
  box-sizing: border-box;
  border: 1px solid rgba(140, 210, 255, 0.65);
  border-radius: 14px;
  background:
    linear-gradient(135deg, rgba(6, 16, 38, 0.92), rgba(20, 24, 70, 0.88));
  box-shadow:
    0 0 24px rgba(70, 170, 255, 0.25),
    inset 0 0 18px rgba(120, 190, 255, 0.08);
  color: rgba(255, 255, 255, 0.94);
  text-align: left;
  transform: translateY(18px);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.28s ease, transform 0.28s ease;
}

.comms-panel.show {
  opacity: 1;
  transform: translateY(0);
}

.comms-label {
  font-size: 12px;
  letter-spacing: 2px;
  color: rgba(120, 210, 255, 0.95);
  margin-bottom: 10px;
  font-weight: 800;
}

.comms-title {
  font-size: 22px;
  font-weight: 900;
  margin-bottom: 10px;
  color: #ffffff;
  text-shadow: 0 0 10px rgba(120, 210, 255, 0.45);
}

.comms-text {
  font-size: 14px;
  line-height: 1.8;
  color: rgba(255,255,255,0.86);
}

.comms-panel::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 14px;
  background: linear-gradient(
    180deg,
    rgba(255,255,255,0.10),
    rgba(255,255,255,0.02) 35%,
    rgba(255,255,255,0.00)
  );
  pointer-events: none;
}

.comms-panel::after {
  content: "";
  position: absolute;
  left: 18px;
  right: 18px;
  top: 48px;
  height: 1px;
  background: linear-gradient(
    90deg,
    rgba(120,210,255,0),
    rgba(120,210,255,0.65),
    rgba(120,210,255,0)
  );
  animation: commsScan 2.4s linear infinite;
  pointer-events: none;
}

@keyframes commsScan {
  0% {
    transform: translateY(0);
    opacity: 0;
  }
  20% {
    opacity: 0.9;
  }
  100% {
    transform: translateY(90px);
    opacity: 0;
  }
}

@keyframes cardShake {
  0%, 100% {
    transform: scale(1.12) translateX(0);
  }
  20% {
    transform: scale(1.12) translateX(-4px);
  }
  40% {
    transform: scale(1.12) translateX(4px);
  }
  60% {
    transform: scale(1.12) translateX(-3px);
  }
  80% {
    transform: scale(1.12) translateX(3px);
  }
}

.carousel-card.shake.active {
  animation: cardShake 0.35s ease;
}

@keyframes cardLaunch {
  0% {
    transform: scale(1.12);
    box-shadow: 0 0 24px rgba(80, 160, 255, 0.45), 0 8px 24px rgba(0,0,0,0.5);
  }
  45% {
    transform: scale(1.20);
    box-shadow: 0 0 38px rgba(170, 210, 255, 0.75), 0 12px 34px rgba(0,0,0,0.58);
  }
  100% {
    transform: scale(1.17);
    box-shadow: 0 0 30px rgba(120, 190, 255, 0.65), 0 10px 30px rgba(0,0,0,0.55);
  }
}

.carousel-card.launch.active {
  animation: cardLaunch 0.45s ease forwards;
}

@media (max-width: 640px) {
  .comms-panel {
    right: 16px;
    bottom: 18px;
  }
}

.carousel-card.active {
  transform: scale(1.12);
  opacity: 1;
  background: #351799;
  box-shadow: 0 0 24px rgba(80, 160, 255, 0.45), 0 8px 24px rgba(0,0,0,0.5);
}

.carousel-card:hover {
  background: #4320b8;
}

.dots {
  margin-top: 12px;
  display: flex;
  justify-content: center;
  gap: 14px;
}

.dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.78);
  background: transparent;
  cursor: pointer;
  padding: 0;
  transition: transform 0.2s ease, background 0.2s ease, opacity 0.2s ease, border-color 0.2s ease;
}

.dot.active {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(255, 255, 255, 0.9);
  transform: scale(1.05);
}

.dot:hover {
  transform: scale(1.08);
  border-color: rgba(255, 255, 255, 1);
}

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

@media (max-width: 900px) {
  .carousel-viewport {
    width: min(700px, 70vw);
  }

  .carousel-track {
    gap: 32px;
  }

  .carousel-card {
    flex-basis: 200px;
    height: 180px;
    font-size: 24px;
  }

  .nav-btn {
    font-size: 60px;
  }
}

@media (max-width: 640px) {
  .school {
    font-size: 16px;
  }

  .title {
    font-size: 24px;
  }

  .year {
    font-size: 28px;
    margin-bottom: 24px;
  }

  .carousel-viewport {
    width: min(520px, 64vw);
  }

  .carousel-card {
    flex-basis: 180px;
    height: 160px;
    font-size: 21px;
  }

  .nav-btn {
    font-size: 48px;
  }
}

</style>
""")
    html.append("</head>")
    html.append("<body>")
    html.append("<div class='space-bg'></div>")
    html.append("<div class='dark-overlay'></div>")
    html.append("<div class='page-fade-overlay' id='page-fade-overlay'></div>")
    html.append("<a class='back-button' href='{}' aria-label='戻る'>×</a>".format(html_escape(back_href)))

    html.append("<div class='page'>")
    html.append("<div class='header'>")
    html.append("<div class='school'>東京理科大学 創域理工学部<br>情報計算科学科</div>")
    html.append("<div class='title'>計算機科学基礎実験<br>計算機科学基礎演習</div>")
    html.append("<div class='year'>2026</div>")
    html.append("</div>")

    html.append("<div class='carousel-shell'>")
    html.append("<button class='nav-btn' id='prev-btn' type='button' aria-label='前へ'>&lsaquo;</button>")
    html.append("<div class='carousel-viewport' id='carousel-viewport'>")
    html.append("<div class='carousel-track' id='carousel-track'>")
    html.append(cards_html)
    html.append("</div>")
    html.append("</div>")
    html.append("<button class='nav-btn' id='next-btn' type='button' aria-label='次へ'>&rsaquo;</button>")
    html.append("</div>")

    html.append("<div class='dots' id='carousel-dots'>")
    html.append(dots_html)
    html.append("</div>")
    html.append("<div class='comms-panel' id='comms-panel'>")
    html.append("<div class='comms-label'>SYSTEM MESSAGE</div>")
    html.append("<div class='comms-title'>Coming Soon...</div>")
    html.append("<div class='comms-text'>この採点ルートは現在準備中です。</div>")
    html.append("</div>")

    html.append("<script>")
    html.append("window.INITIAL_CAROUSEL_INDEX = {};".format(initial_index))
    html.append("""
document.addEventListener('DOMContentLoaded', function () {
  const viewport = document.getElementById('carousel-viewport');
  const track = document.getElementById('carousel-track');
  const cards = Array.from(document.querySelectorAll('.carousel-card'));
  const dots = Array.from(document.querySelectorAll('.dot'));
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const commsPanel = document.getElementById('comms-panel');
  const fadeOverlay = document.getElementById('page-fade-overlay');
  let commsTimer = null;

  let currentIndex = window.INITIAL_CAROUSEL_INDEX || 0;

  function clampIndex(index) {
    if (index < 0) return 0;
    if (index > cards.length - 1) return cards.length - 1;
    return index;
  }

  function updateCarousel(index) {
    currentIndex = clampIndex(index);

    cards.forEach(function (card, i) {
      card.classList.toggle('active', i === currentIndex);
    });

    dots.forEach(function (dot, i) {
      dot.classList.toggle('active', i === currentIndex);
    });

    const activeCard = cards[currentIndex];
    const viewportWidth = viewport.clientWidth;
    const activeCenter = activeCard.offsetLeft + (activeCard.offsetWidth / 2);
    const offset = (viewportWidth / 2) - activeCenter;

    track.style.transform = 'translateX(' + offset + 'px)';

    prevBtn.disabled = currentIndex === 0;
    nextBtn.disabled = currentIndex === cards.length - 1;
  }

　function showCommsMessage(card) {
　  if (card) {
　    const index = parseInt(card.getAttribute('data-index'), 10);
 　   updateCarousel(index);

 　   card.classList.remove('shake');
 　   void card.offsetWidth;
　    card.classList.add('shake');
 　 }

　  commsPanel.classList.add('show');

 　 if (commsTimer) {
 　   clearTimeout(commsTimer);
　  }

　  commsTimer = setTimeout(function () {
 　   commsPanel.classList.remove('show');
 　 }, 4200);
　}

  prevBtn.addEventListener('click', function () {
    updateCarousel(currentIndex - 1);
  });

  nextBtn.addEventListener('click', function () {
    updateCarousel(currentIndex + 1);
  });

  dots.forEach(function (dot) {
    dot.addEventListener('click', function () {
      const index = parseInt(dot.getAttribute('data-index'), 10);
      updateCarousel(index);
    });
  });

  cards.forEach(function (card) {
    card.addEventListener('mouseenter', function () {
      const index = parseInt(card.getAttribute('data-index'), 10);
      updateCarousel(index);
    });
  });

  cards.forEach(function (card) {
    card.addEventListener('click', function (e) {
      if (card.classList.contains('coming-soon-card')) {
        e.preventDefault();
        showCommsMessage(card);
        return;
      }

      const href = card.getAttribute('href');

      if (href && href !== '#') {
        e.preventDefault();

        const index = parseInt(card.getAttribute('data-index'), 10);
        updateCarousel(index);

        card.classList.remove('launch');
        void card.offsetWidth;
        card.classList.add('launch');

        if (href === '/upload') {
          setTimeout(function () {
            fadeOverlay.classList.add('show');
          }, 180);

          setTimeout(function () {
            window.location.href = href;
          }, 1300);
        } else {
          setTimeout(function () {
            window.location.href = href;
          }, 450);
        }
      }
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') {
      updateCarousel(currentIndex - 1);
    } else if (e.key === 'ArrowRight') {
      updateCarousel(currentIndex + 1);
    }
  });

  let touchStartX = 0;

  viewport.addEventListener('touchstart', function (e) {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  viewport.addEventListener('touchend', function (e) {
    const touchEndX = e.changedTouches[0].screenX;
    const diff = touchStartX - touchEndX;

    if (diff > 40) {
      updateCarousel(currentIndex + 1);
    } else if (diff < -40) {
      updateCarousel(currentIndex - 1);
    }
  }, { passive: true });

  window.addEventListener('resize', function () {
    updateCarousel(currentIndex);
  });

  updateCarousel(currentIndex);
});
""")
    html.append("</script>")
    html.append("</body>")
    html.append("</html>")

    return "\n".join(html)


def build_index_html(message=""):
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='ja'>")
    html.append("<head>")
    html.append("<meta charset='UTF-8'>")
    html.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append("<title>OCaml 1期</title>")
    html.append("""
<style>
:root {
  --poster-mint: #86ddb1;
  --poster-mint-dark: #33a76c;
  --poster-ink: #0b0b0d;
  --poster-paper: #f1f1ef;
  --poster-muted: #626262;
  --poster-card: rgba(255, 255, 255, 0.88);
  --poster-red: #ff454f;
  --poster-orange: #ffb36d;
}

* {
  box-sizing: border-box;
}

body {
  min-height: 100vh;
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", sans-serif;
  color: var(--poster-ink);
  background:
    radial-gradient(circle at 72% 22%, rgba(255, 69, 79, 0.34), transparent 12rem),
    linear-gradient(
      180deg,
      var(--poster-paper) 0,
      var(--poster-paper) 560px,
      var(--poster-mint) 560px,
      var(--poster-mint) 100%
    );
}

.upload-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  padding: 42px 24px 56px;
}

.upload-back-link {
  position: relative;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  width: fit-content;
  margin-bottom: 28px;
  padding: 10px 18px;
  border: 2px solid var(--poster-ink);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--poster-ink);
  text-decoration: none;
  font-size: 14px;
  font-weight: 900;
  letter-spacing: 0.02em;
  box-shadow: 0 10px 24px rgba(11, 11, 13, 0.08);
  transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.upload-back-link::before {
  content: "";
  display: inline-block;
  width: 0;
  height: 0;
  border-top: 7px solid transparent;
  border-bottom: 7px solid transparent;
  border-right: 11px solid var(--poster-ink);
}

.upload-back-link:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 28px rgba(11, 11, 13, 0.14);
}

.guide-menu-wrap {
  position: absolute;
  top: 42px;
  right: 24px;
  z-index: 20;
}

.guide-menu-button {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 0;
  background: transparent;
  color: var(--poster-ink);
  font-size: 32px;
  font-weight: 900;
  line-height: 1;
  cursor: pointer;
  box-shadow: none;
  backdrop-filter: none;
  transition:
    transform 0.2s ease,
    opacity 0.2s ease;
}

.guide-menu-button:hover {
  transform: translateY(-1px);
  background: transparent;
  box-shadow: none;
  opacity: 0.72;
}

.guide-menu-panel {
  position: absolute;
  top: 54px;
  right: 0;
  width: 190px;
  padding: 8px;
  border: 1px solid rgba(11, 11, 13, 0.12);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 18px 42px rgba(11, 11, 13, 0.16);
  backdrop-filter: blur(16px);
  opacity: 0;
  transform: translateY(-6px) scale(0.98);
  pointer-events: none;
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}

.guide-menu-wrap.open .guide-menu-panel {
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: auto;
}

.guide-menu-item {
  width: 100%;
  border: none;
  border-radius: 12px;
  padding: 12px 14px;
  background: transparent;
  color: rgba(11, 11, 13, 0.82);
  text-align: left;
  font-size: 14px;
  font-weight: 900;
  cursor: pointer;
  transition:
    background 0.18s ease,
    transform 0.18s ease;
}

.guide-menu-item:hover {
  background: rgba(134, 221, 177, 0.22);
  transform: translateX(2px);
}

.guide-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1400;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(11, 11, 13, 0.38);
  backdrop-filter: blur(10px);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.22s ease;
}

.guide-modal-overlay.show {
  opacity: 1;
  pointer-events: auto;
}

.guide-modal {
  width: min(760px, 100%);
  max-height: min(82vh, 760px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 28px;
  border: 2px solid var(--poster-ink);
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 28px 70px rgba(11, 11, 13, 0.28);
}

.guide-modal-title {
  margin: 0 0 16px;
  color: var(--poster-ink);
  font-size: 28px;
  font-weight: 950;
  letter-spacing: -0.04em;
}

.guide-modal-content {
  min-height: 0;
  overflow-y: auto;
  padding-right: 8px;
  color: rgba(11, 11, 13, 0.76);
}

.guide-list {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.guide-card {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(134, 221, 177, 0.16);
  border: 1px solid rgba(37, 138, 89, 0.14);
}

.guide-card-title {
  margin: 0 0 6px;
  color: var(--poster-ink);
  font-size: 15px;
  font-weight: 950;
}

.guide-card-text {
  margin: 0;
  line-height: 1.7;
  font-size: 14px;
  font-weight: 700;
}

.guide-subitems {
  margin-top: 14px;
}

.guide-subitem {
  padding-top: 14px;
}

.guide-subitem + .guide-subitem {
  margin-top: 14px;
  border-top: 1px solid rgba(37, 138, 89, 0.16);
}

.guide-intro {
  margin: 0 0 16px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(134, 221, 177, 0.14);
  border: 1px solid rgba(37, 138, 89, 0.14);
  color: rgba(11, 11, 13, 0.78);
  line-height: 1.8;
  font-size: 14px;
  font-weight: 750;
}

.guide-section-title {
  margin: 18px 0 10px;
  color: var(--poster-ink);
  font-size: 16px;
  font-weight: 950;
}

.guide-card-code {
  margin: 8px 0 0;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(11, 11, 13, 0.06);
  color: rgba(11, 11, 13, 0.76);
  font-family: Consolas, "Courier New", monospace;
  font-size: 12px;
  line-height: 1.7;
  white-space: pre-wrap;
  overflow-x: auto;
  text-align: left;
}

.guide-image-wrap {
  margin: 12px 0;
  padding: 12px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(11, 11, 13, 0.10);
}

.guide-image {
  display: block;
  width: min(100%, 460px);
  height: auto;
  margin: 0 auto;
  border-radius: 12px;
}

.guide-submit-list {
  margin: 8px 0 0;
  padding-left: 1.2em;
  line-height: 1.8;
  font-size: 14px;
  font-weight: 700;
}

.guide-status-grid {
  display: grid;
  gap: 12px;
}

.guide-status-card {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid rgba(11, 11, 13, 0.10);
}

.guide-status-label {
  display: inline-flex;
  margin-bottom: 8px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 950;
}

.guide-status-label.ok {
  background: rgba(37, 138, 89, 0.12);
  color: var(--poster-mint-dark);
}

.guide-status-label.ng {
  background: rgba(255, 107, 72, 0.14);
  color: #c63c1c;
}

.guide-status-label.warning {
  background: rgba(255, 184, 77, 0.20);
  color: #9a6200;
}

.guide-status-label.error {
  background: rgba(198, 40, 40, 0.12);
  color: var(--poster-error);
}

.guide-modal-actions {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.guide-modal-close {
  min-width: 120px;
  border: 2px solid var(--poster-ink);
  border-radius: 999px;
  padding: 11px 18px;
  background: var(--poster-ink);
  color: white;
  font-size: 14px;
  font-weight: 950;
  cursor: pointer;
  box-shadow: 0 12px 26px rgba(11, 11, 13, 0.22);
  transition:
    transform 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease;
}

.guide-modal-close:hover {
  transform: translateY(-2px);
  background: #1f1f22;
  box-shadow: 0 16px 30px rgba(11, 11, 13, 0.26);
}

.upload-page::before {
  content: "";
  position: absolute;
  top: -90px;
  right: max(40px, 11vw);
  width: 310px;
  height: 230px;
  border-radius: 48% 52% 45% 55%;
  background:
    radial-gradient(circle at 68% 12%, rgba(148, 239, 199, 0.82), transparent 18%),
    radial-gradient(circle at 46% 42%, var(--poster-red), rgba(255, 69, 79, 0.88) 42%, transparent 72%),
    radial-gradient(circle at 28% 70%, var(--poster-orange), transparent 45%);
  filter: blur(20px);
  opacity: 0.95;
  transform: rotate(4deg);
}

.hero {
  position: relative;
  z-index: 1;
  width: min(1040px, 100%);
  margin: 0 auto;
}

.hero-top {
  min-height: 260px;
  display: grid;
  grid-template-columns: minmax(220px, 0.86fr) minmax(280px, 1.14fr);
  gap: 36px;
  align-items: end;
  padding-bottom: 34px;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  width: fit-content;
  padding: 7px 12px;
  border: 2px solid var(--poster-ink);
  border-radius: 999px;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.04em;
  margin-bottom: 22px;
}

.badge::before {
  content: "TA";
  display: grid;
  place-items: center;
  width: 30px;
  height: 20px;
  border-radius: 999px;
  background: var(--poster-ink);
  color: white;
  font-size: 11px;
}

h1 {
  margin: 0;
  font-size: clamp(48px, 9vw, 104px);
  line-height: 0.92;
  letter-spacing: -0.075em;
  font-weight: 950;
}

.hero-copy {
  align-self: center;
  max-width: 560px;
}

.kicker {
  margin: 0 0 16px;
  color: var(--poster-muted);
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.lead {
  margin: 0;
  font-size: clamp(17px, 2.1vw, 22px);
  font-weight: 750;
  line-height: 1.85;
}

.work-panel {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(260px, 0.86fr) minmax(320px, 1.14fr);
  gap: 30px;
  align-items: stretch;
  margin-top: 18px;
}

.info-block {
  padding: 26px 4px 0;
}

.info-block h2 {
  margin: 0 0 14px;
  font-size: clamp(30px, 5vw, 54px);
  line-height: 1.08;
  letter-spacing: -0.05em;
  font-weight: 950;
}

.info-block p {
  margin: 0;
  color: rgba(11, 11, 13, 0.74);
  font-size: 16px;
  line-height: 1.85;
  font-weight: 650;
}

.upload-card {
  position: relative;
  padding: clamp(24px, 4vw, 36px);
  border: 1px solid rgba(255, 255, 255, 0.78);
  border-radius: 30px;
  background: var(--poster-card);
  box-shadow: 0 24px 60px rgba(24, 88, 59, 0.22);
  backdrop-filter: blur(16px);
}

.steps {
  display: grid;
  gap: 12px;
  margin: 0 0 28px;
  padding: 0;
  list-style: none;
}

.steps li {
  display: grid;
  grid-template-columns: 42px 1fr;
  gap: 13px;
  align-items: start;
  color: rgba(11, 11, 13, 0.78);
  font-size: 15px;
  line-height: 1.65;
  font-weight: 650;
}

.step-num {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: var(--poster-ink);
  color: white;
  font-size: 14px;
  font-weight: 900;
}

.form-title {
  margin: 0 0 12px;
  font-size: 18px;
  font-weight: 900;
}

.file-drop {
  display: block;
  margin: 0 0 18px;
  padding: 22px;
  border: 2px dashed rgba(11, 11, 13, 0.28);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.74);
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.file-drop:hover {
  transform: translateY(-2px);
  border-color: var(--poster-mint-dark);
  background: rgba(255, 255, 255, 0.94);
}

.file-drop.is-dragging {
  transform: translateY(-2px);
  border-color: var(--poster-mint-dark);
  background: rgba(255, 255, 255, 0.94);
}

.file-drop input[type="file"] {
  width: 100%;
  margin-top: 14px;
  color: rgba(11, 11, 13, 0.72);
  font-weight: 700;
}

.file-drop-title {
  display: block;
  font-size: 17px;
  font-weight: 900;
}

.file-drop-text {
  display: block;
  margin-top: 6px;
  color: rgba(11, 11, 13, 0.58);
  font-size: 13px;
  line-height: 1.6;
}

.selected-files {
  margin: 0 0 20px;
  padding: 16px 18px;
  border-radius: 20px;
  background: rgba(134, 221, 177, 0.28);
  border: 1px solid rgba(51, 167, 108, 0.28);
}

.selected-files-title {
  margin: 0 0 8px;
  color: rgba(11, 11, 13, 0.74);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.04em;
}

.selected-files-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 0 0 8px;
}

.selected-files-header .selected-files-title {
  margin: 0;
}

.clear-files-button {
  display: none;
  flex: 0 0 auto;
  border: 1px solid rgba(11, 11, 13, 0.20);
  border-radius: 999px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.70);
  color: rgba(11, 11, 13, 0.72);
  font-size: 12px;
  font-weight: 900;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.clear-files-button.show {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.clear-files-button:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 8px 18px rgba(11, 11, 13, 0.08);
}

.selected-files ul {
  margin: 0;
  padding-left: 20px;
  color: rgba(11, 11, 13, 0.82);
  font-size: 14px;
  line-height: 1.7;
  font-weight: 700;
  word-break: break-all;
}

.selected-files.is-empty ul {
  padding-left: 0;
  list-style: none;
  color: rgba(11, 11, 13, 0.48);
}

.selected-file-item {
  cursor: pointer;
  width: fit-content;
  padding: 4px 8px;
  border-radius: 999px;
  transition: background 0.2s ease, transform 0.2s ease;
}

.selected-file-item:hover {
  background: rgba(255, 255, 255, 0.62);
  transform: translateX(2px);
}

.delete-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(11, 11, 13, 0.38);
  backdrop-filter: blur(10px);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.22s ease;
}

.delete-modal-overlay.show {
  opacity: 1;
  pointer-events: auto;
}

.issue-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1300;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(11, 11, 13, 0.38);
  backdrop-filter: blur(10px);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.22s ease;
}

.issue-modal-overlay.show {
  opacity: 1;
  pointer-events: auto;
}

.issue-modal {
  width: min(720px, 100%);
  max-height: min(82vh, 720px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 28px;
  border: 2px solid var(--poster-ink);
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 28px 70px rgba(11, 11, 13, 0.28);
}

.issue-modal-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.issue-modal-status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 13px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 950;
}

.issue-modal-status.wrong {
  background: var(--poster-alert-soft);
  color: #c63c1c;
}

.issue-modal-status.warning {
  background: var(--poster-warning-soft);
  color: #9a6200;
}

.issue-modal-status.error {
  background: var(--poster-error-soft);
  color: var(--poster-error);
}

.issue-modal-question {
  font-size: 26px;
  font-weight: 950;
  letter-spacing: -0.04em;
}

.issue-modal-content {
  color: rgba(11, 11, 13, 0.76);
}

.issue-modal-content > p {
  margin: 0 0 14px;
  line-height: 1.7;
  font-weight: 750;
}

.issue-modal-actions {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.issue-modal-close {
  min-width: 120px;
  border: 2px solid var(--poster-ink);
  border-radius: 999px;
  padding: 11px 18px;
  background: var(--poster-ink);
  color: white;
  font-size: 14px;
  font-weight: 950;
  cursor: pointer;
  box-shadow: 0 12px 26px rgba(11, 11, 13, 0.22);
  transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.issue-modal-close:hover {
  transform: translateY(-2px);
  background: #1f1f22;
  box-shadow: 0 16px 30px rgba(11, 11, 13, 0.26);
}

.delete-modal {
  width: min(420px, 100%);
  padding: 30px 28px;
  border: 2px solid var(--poster-ink);
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 28px 70px rgba(11, 11, 13, 0.28);
  text-align: center;
}

.delete-modal-title {
  margin: 0 0 10px;
  font-size: 24px;
  font-weight: 950;
  letter-spacing: -0.04em;
}

.delete-modal-text {
  margin: 0 0 22px;
  color: rgba(11, 11, 13, 0.66);
  font-size: 14px;
  font-weight: 750;
  line-height: 1.7;
  word-break: break-all;
}

.delete-modal-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.delete-modal-button {
  min-width: 120px;
  border: 2px solid var(--poster-ink);
  border-radius: 999px;
  padding: 11px 18px;
  font-size: 14px;
  font-weight: 950;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.delete-modal-button:hover {
  transform: translateY(-2px);
}

.delete-modal-button.cancel {
  background: rgba(255, 255, 255, 0.76);
  color: var(--poster-ink);
}

.delete-modal-button.delete {
  background: var(--poster-ink);
  color: white;
  box-shadow: 0 12px 26px rgba(11, 11, 13, 0.22);
}

.submit-button {
  width: 100%;
  border: none;
  border-radius: 999px;
  padding: 16px 22px;
  background: var(--poster-ink);
  color: white;
  font-size: 17px;
  font-weight: 950;
  cursor: pointer;
  box-shadow: 0 14px 28px rgba(11, 11, 13, 0.24);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.submit-button:hover {
  transform: translateY(-2px);
  background: #1f1f22;
  box-shadow: 0 18px 32px rgba(11, 11, 13, 0.30);
}

.mode-switch-block {
  margin: 0 0 18px;
}

.mode-switch-title {
  margin: 0 0 8px;
  color: rgba(11, 11, 13, 0.68);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.04em;
}

.mode-switch {
  display: inline-flex;
  padding: 4px;
  border: 1px solid rgba(11, 11, 13, 0.16);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.62);
  box-shadow: 0 10px 22px rgba(11, 11, 13, 0.06);
}

.mode-switch-button {
  border: none;
  border-radius: 999px;
  padding: 9px 16px;
  background: transparent;
  color: rgba(11, 11, 13, 0.68);
  font-size: 13px;
  font-weight: 950;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.mode-switch-button.active {
  background: var(--poster-mint);
  color: var(--poster-ink);
  box-shadow: 0 10px 22px rgba(51, 167, 108, 0.22);
}

.mode-switch-button:hover {
  transform: translateY(-1px);
}

.student-upload-panel {
  margin: 0 0 20px;
  padding: 18px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.64);
  border: 1px solid rgba(11, 11, 13, 0.10);
}

.student-panel-heading {
  margin-bottom: 16px;
}

.student-panel-title {
  margin: 0 0 6px;
  font-size: 17px;
  font-weight: 950;
}

.student-panel-text {
  margin: 0;
  color: rgba(11, 11, 13, 0.58);
  font-size: 13px;
  line-height: 1.6;
  font-weight: 650;
}

.student-upload-head,
.student-upload-row {
  display: grid;
  grid-template-columns: minmax(120px, 0.8fr) minmax(220px, 1.6fr);
  gap: 12px;
  align-items: center;
}

.student-upload-head {
  margin: 0 0 8px;
  padding: 0 12px;
  color: rgba(11, 11, 13, 0.62);
  font-size: 12px;
  font-weight: 950;
  letter-spacing: 0.04em;
}

.student-upload-row {
  position: relative;
  margin-bottom: 12px;
  padding: 12px;
  border: 1px solid rgba(11, 11, 13, 0.14);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 8px 20px rgba(11, 11, 13, 0.06);
  transition:
    transform 0.2s ease,
    background 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.student-upload-row:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 10px 24px rgba(11, 11, 13, 0.09);
}

.student-upload-row.is-dragging-file {
  border-color: var(--poster-mint-dark);
  background: rgba(134, 221, 177, 0.24);
  box-shadow: 0 12px 28px rgba(51, 167, 108, 0.20);
}

.student-upload-row.is-invalid-file {
  border-color: var(--poster-red);
  background: rgba(255, 69, 79, 0.10);
  animation: studentCardShake 0.28s ease;
}

.student-upload-row.is-sort-ready {
  border-color: rgba(51, 167, 108, 0.38);
  background: rgba(255, 255, 255, 0.90);
  box-shadow: 0 12px 28px rgba(51, 167, 108, 0.12);
  cursor: grab;
}

.student-upload-row.is-sorting {
  cursor: grabbing;
}

body.student-sorting-active {
  user-select: none;
}

body.student-sorting-active,
body.student-sorting-active * {
  cursor: grabbing !important;
}

body.student-sorting-active .student-file-input,
body.student-sorting-active .student-file-input::file-selector-button,
body.student-sorting-active .student-file-input::-webkit-file-upload-button {
  cursor: grabbing !important;
}

body.student-sorting-active .student-upload-row {
  transition:
    transform 0.16s ease,
    background 0.16s ease,
    border-color 0.16s ease,
    box-shadow 0.16s ease;
}

body.student-sorting-active .student-upload-row.is-dragging-file {
  border-color: rgba(11, 11, 13, 0.14);
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 8px 20px rgba(11, 11, 13, 0.06);
}

.student-upload-row.is-ghost-source {
  opacity: 0.36;
  background: rgba(255, 255, 255, 0.54);
  border-style: dashed;
  box-shadow: none;
}

.student-sort-placeholder {
  height: 0;
  margin-bottom: 12px;
  border: 1px dashed rgba(51, 167, 108, 0.42);
  border-radius: 18px;
  background:
    linear-gradient(
      135deg,
      rgba(134, 221, 177, 0.18),
      rgba(255, 255, 255, 0.42)
    );
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.50),
    0 8px 18px rgba(51, 167, 108, 0.08);
  transition:
    height 0.16s ease,
    background 0.16s ease,
    border-color 0.16s ease,
    box-shadow 0.16s ease;
}

.student-upload-row,
.student-sort-placeholder {
  will-change: transform;
}

.student-upload-row.is-list-moving,
.student-sort-placeholder.is-list-moving {
  transition: transform 0.18s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.student-delete-slide-area {
  --delete-progress: 0;
  position: absolute;
  inset: 0;
  z-index: 0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 18px;
  border-radius: 18px;
  background:
    linear-gradient(
      90deg,
      rgba(255, 69, 79, 0.02),
      rgba(255, 69, 79, calc(0.06 + 0.18 * var(--delete-progress)))
    );
  color: rgba(198, 40, 40, calc(0.42 + 0.38 * var(--delete-progress)));
  font-size: 13px;
  font-weight: 950;
  letter-spacing: 0.04em;
  opacity: calc(0.18 + 0.82 * var(--delete-progress));
  transform: scale(calc(0.985 + 0.015 * var(--delete-progress)));
  transition:
    opacity 0.08s linear,
    transform 0.08s linear,
    background 0.08s linear,
    color 0.08s linear;
  pointer-events: none;
}

.student-delete-slide-area::after {
  content: "削除";
  color: rgba(198, 40, 40, calc(0.48 + 0.38 * var(--delete-progress)));
  font-size: 13px;
  font-weight: 950;
  letter-spacing: 0.08em;
  opacity: calc(0.42 + 0.58 * var(--delete-progress));
  transition:
    opacity 0.08s linear,
    color 0.08s linear;
}

.student-sort-placeholder.has-delete-slide-area {
  position: relative;
  overflow: hidden;
  border-color: rgba(255, 69, 79, calc(0.14 + 0.22 * var(--delete-progress, 0)));
  background: rgba(255, 255, 255, 0.42);
}

.student-drag-ghost.is-delete-ready {
  border-color: rgba(255, 69, 79, 0.54);
  background:
    linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.98),
      rgba(255, 69, 79, 0.08)
    );
  box-shadow:
    0 24px 54px rgba(11, 11, 13, 0.18),
    0 0 0 4px rgba(255, 69, 79, 0.14);
}

.student-upload-row.is-drop-landed {
  animation: studentRowLanded 0.18s ease-out;
}

@keyframes studentRowLanded {
  0% {
    opacity: 0.82;
    transform: translate3d(0, 2px, 0);
  }

  100% {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
}

.student-drag-ghost {
  position: fixed;
  left: 0;
  top: 0;
  z-index: 2000;
  pointer-events: none;
  margin: 0;
  opacity: 0.98;
  background: rgba(255, 255, 255, 0.98);
  border-color: rgba(51, 167, 108, 0.52);
  box-shadow:
    0 24px 54px rgba(11, 11, 13, 0.20),
    0 0 0 4px rgba(134, 221, 177, 0.18);
  transform: translate3d(0, 0, 0) scale(1.015);
  transition: none;
}

.student-drag-ghost input,
.student-drag-ghost button {
  pointer-events: none;
}

.student-drag-ghost-pickup {
  animation: studentGhostPickup 0.16s ease;
}

.student-drag-ghost.is-dropping {
  opacity: 0.92;
  transform: translate3d(0, 0, 0) scale(1);
  box-shadow:
    0 10px 26px rgba(11, 11, 13, 0.12),
    0 0 0 2px rgba(134, 221, 177, 0.12);
  transition:
    left 0.20s cubic-bezier(0.2, 0.8, 0.2, 1),
    top 0.20s cubic-bezier(0.2, 0.8, 0.2, 1),
    width 0.20s cubic-bezier(0.2, 0.8, 0.2, 1),
    height 0.20s cubic-bezier(0.2, 0.8, 0.2, 1),
    transform 0.20s cubic-bezier(0.2, 0.8, 0.2, 1),
    opacity 0.20s ease,
    box-shadow 0.20s ease;
}

@keyframes studentGhostPickup {
  0% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  70% {
    transform: translate3d(0, -3px, 0) scale(1.02);
  }
  100% {
    transform: translate3d(0, 0, 0) scale(1.015);
  }
}

@keyframes studentCardShake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-4px);
  }
  50% {
    transform: translateX(4px);
  }
  75% {
    transform: translateX(-3px);
  }
}

.student-id-input {
  width: 100%;
  border: 1px solid rgba(11, 11, 13, 0.18);
  border-radius: 14px;
  padding: 11px 12px;
  background: rgba(255, 255, 255, 0.78);
  color: var(--poster-ink);
  font-size: 14px;
  font-weight: 800;
}

.student-file-input {
  position: static;
  flex: 0 0 112px;
  width: 112px;
  min-width: 112px;
  max-width: 112px;
  height: auto;
  opacity: 1;
  pointer-events: auto;
  color: transparent;
  font-size: 13px;
}

.student-file-control {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  width: 100%;
}

.student-file-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: rgba(11, 11, 13, 0.78);
  font-size: 14px;
  font-weight: 750;
  line-height: 1.6;
  cursor: grab;
}

.add-student-row-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  border: 1px solid rgba(11, 11, 13, 0.20);
  border-radius: 999px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.72);
  color: rgba(11, 11, 13, 0.74);
  font-size: 13px;
  font-weight: 950;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.add-student-row-button:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 8px 18px rgba(11, 11, 13, 0.08);
}

.note {
  margin: 18px 0 0;
  color: rgba(11, 11, 13, 0.56);
  font-size: 13px;
  line-height: 1.7;
}

.message {
  margin: 0 0 18px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 69, 79, 0.12);
  color: #b01825;
  font-weight: 900;
}

.loading-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(241, 241, 239, 0.82);
  backdrop-filter: blur(10px);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
}

.loading-overlay.show {
  opacity: 1;
  pointer-events: auto;
}

.result-frame-overlay {
  position: fixed;
  inset: 0;
  z-index: 1500;
  background: var(--poster-paper);
}

body.result-frame-open {
  overflow: hidden;
}

.result-frame-overlay[hidden] {
  display: none;
}

.result-frame {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
  background: white;
}

.loading-card {
  width: min(380px, 100%);
  padding: 34px 30px;
  border: 2px solid var(--poster-ink);
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 24px 60px rgba(11, 11, 13, 0.22);
  text-align: center;
}

.loading-ring {
  width: 52px;
  height: 52px;
  margin: 0 auto 20px;
  border: 5px solid rgba(11, 11, 13, 0.12);
  border-top-color: var(--poster-ink);
  border-radius: 50%;
  animation: loadingSpin 0.85s linear infinite;
}

.loading-title {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 950;
  letter-spacing: -0.04em;
}

.loading-text {
  margin: 0;
  color: rgba(11, 11, 13, 0.62);
  font-size: 14px;
  font-weight: 750;
  line-height: 1.7;
}

@keyframes loadingSpin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 780px) {
  .upload-page {
    padding: 28px 18px 40px;
  }

  .upload-page::after {
    display: none;
  }

  .hero-top,
  .work-panel {
    grid-template-columns: 1fr;
  }

  .hero-top {
    min-height: auto;
    gap: 24px;
  }

  .info-block {
    padding-top: 0;
  }
}
</style>
""")
    html.append("</head>")
    html.append("<body>")
    html.append("<main class='upload-page'>")
    html.append("<a class='upload-back-link' href='/period'>選択画面へ戻る</a>")
    html.append("<div class='guide-menu-wrap' id='guide-menu-wrap'>")
    html.append("<button class='guide-menu-button' id='guide-menu-button' type='button' aria-label='課題一覧と採点基準を開く'>☰</button>")
    html.append("<div class='guide-menu-panel' id='guide-menu-panel'>")
    html.append("<button class='guide-menu-item' type='button' data-guide='tasks'>課題内容</button>")
    html.append("<button class='guide-menu-item' type='button' data-guide='criteria'>採点基準</button>")
    html.append("</div>")
    html.append("</div>")
    html.append("<section class='hero'>")
    html.append("<div class='hero-top'>")
    html.append("<div>")
    html.append("<div class='badge'>Report Checker</div>")
    html.append("<h1>OCaml<br>1期</h1>")
    html.append("</div>")
    html.append("<div class='hero-copy'>")
    html.append("<p class='kicker'>SUBMISSION CHECKER</p>")
    html.append("<p class='lead'>OCaml課題の .ml ファイルを自動でテストし、各大問の判定結果をわかりやすく表示します。</p>")
    html.append("</div>")
    html.append("</div>")

    html.append("<div class='work-panel'>")
    html.append("<div class='info-block'>")
    html.append("<h2>採点作業を、<br>シンプルに。</h2>")
    html.append("<p>複数ファイルにも対応しています。選択後にファイル名一覧が表示されるので、採点前に対象ファイルを確認できます。</p>")
    html.append("</div>")

    html.append("<div class='upload-card'>")
    if message:
        html.append("<p class='message'>{}</p>".format(html_escape(message)))

    html.append("<ol class='steps' aria-label='使い方'>")
    html.append("<li><span class='step-num'>01</span><span>課題の .ml ファイルを選択します。</span></li>")
    html.append("<li><span class='step-num'>02</span><span>選択済みファイル名を確認します。</span></li>")
    html.append("<li><span class='step-num'>03</span><span>採点を実行し、結果画面で大問ごとの判定を確認します。</span></li>")
    html.append("</ol>")

    html.append("<form id='upload-form' method='POST' enctype='multipart/form-data' action='/check' target='result-frame'>")
    html.append("<p class='form-title'>ファイルの選択</p>")
    html.append("<input type='hidden' name='upload_mode' id='upload-mode-input' value='bulk'>")

    html.append("<div class='mode-switch-block'>")
    html.append("<p class='mode-switch-title'>採点方法</p>")
    html.append("<div class='mode-switch' role='tablist' aria-label='採点方法'>")
    html.append("<button class='mode-switch-button active' type='button' id='bulk-mode-button'>一括アップロード</button>")
    html.append("<button class='mode-switch-button' type='button' id='student-mode-button'>学籍番号ごと</button>")
    html.append("</div>")
    html.append("</div>")

    html.append("<div id='bulk-upload-panel'>")
    html.append("<label class='file-drop'>")
    html.append("<span class='file-drop-title'>.ml ファイルをアップロード</span>")
    html.append("<span class='file-drop-text'>複数選択できます。選択したファイル名は下に表示されます。</span>")
    html.append("<input id='file-input' type='file' name='files' accept='.ml' multiple>")
    html.append("</label>")

    html.append("<div class='selected-files is-empty' id='selected-files' aria-live='polite'>")
    html.append("<div class='selected-files-header'>")
    html.append("<p class='selected-files-title'>選択中のファイル</p>")
    html.append("<button class='clear-files-button' id='clear-files-button' type='button'>すべてクリア</button>")
    html.append("</div>")
    html.append("<ul id='selected-file-list'><li>まだファイルが選択されていません。</li></ul>")
    html.append("</div>")
    html.append("</div>")

    html.append("<div id='student-upload-panel' class='student-upload-panel' hidden>")
    html.append("<div class='student-panel-heading'>")
    html.append("<p class='student-panel-title'>学籍番号ごとにファイルを登録</p>")
    html.append("<p class='student-panel-text'>学籍番号と対応する .ml ファイルを選択してください。</p>")
    html.append("</div>")

    html.append("<div class='student-upload-head'>")
    html.append("<span>学籍番号</span>")
    html.append("<span>ファイル</span>")
    html.append("<span></span>")
    html.append("</div>")

    html.append("<div id='student-upload-rows'></div>")
    html.append("<button class='add-student-row-button' type='button' id='add-student-row-button'>＋ 行を追加</button>")
    html.append("</div>")

    html.append("<button class='submit-button' type='submit'>採点を実行</button>")
    html.append("</form>")

    html.append("<p class='note'>")
    html.append("注意: Exception が出る実行例を提出ファイル内で直接実行している場合、読み込み時点でエラーになることがあります。")
    html.append("課題文の指示通り、例外が出る呼び出しはコメントアウトしてください。")
    html.append("</p>")
    html.append("</div>")
    html.append("</div>")
    html.append("</section>")
    html.append("</main>")

    html.append("<div class='guide-modal-overlay' id='guide-modal-overlay' aria-hidden='true'>")
    html.append("<div class='guide-modal' role='dialog' aria-modal='true' aria-labelledby='guide-modal-title'>")
    html.append("<h2 class='guide-modal-title' id='guide-modal-title'></h2>")
    html.append("<div class='guide-modal-content' id='guide-modal-content'></div>")
    html.append("<div class='guide-modal-actions'>")
    html.append("<button class='guide-modal-close' type='button' id='guide-modal-close'>閉じる</button>")
    html.append("</div>")
    html.append("</div>")
    html.append("</div>")

    html.append("<div class='delete-modal-overlay' id='delete-modal-overlay' aria-hidden='true'>")
    html.append("<div class='delete-modal' role='dialog' aria-modal='true' aria-labelledby='delete-modal-title'>")
    html.append("<p class='delete-modal-title' id='delete-modal-title'>このファイルを削除しますか？</p>")
    html.append("<p class='delete-modal-text' id='delete-modal-text'></p>")
    html.append("<div class='delete-modal-actions'>")
    html.append("<button class='delete-modal-button cancel' type='button' id='delete-cancel-button'>キャンセル</button>")
    html.append("<button class='delete-modal-button delete' type='button' id='delete-confirm-button'>削除</button>")
    html.append("</div>")
    html.append("</div>")
    html.append("</div>")
    html.append("<div class='loading-overlay' id='loading-overlay' aria-live='polite'>")
    html.append("<div class='loading-card'>")
    html.append("<div class='loading-ring' aria-hidden='true'></div>")
    html.append("<p class='loading-title'>採点中...</p>")
    html.append("<p class='loading-text'>提出ファイルをチェックしています。<br>しばらくお待ちください。</p>")
    html.append("</div>")
    html.append("</div>")
    html.append("<div class='result-frame-overlay' id='result-frame-overlay' hidden>")
    html.append("<iframe class='result-frame' id='result-frame' name='result-frame' title='採点結果'></iframe>")
    html.append("</div>")
    html.append("""
<script>
document.addEventListener('DOMContentLoaded', function () {
  const guideMenuWrap = document.getElementById('guide-menu-wrap');
  const guideMenuButton = document.getElementById('guide-menu-button');
  const guideModalOverlay = document.getElementById('guide-modal-overlay');
  const guideModalTitle = document.getElementById('guide-modal-title');
  const guideModalContent = document.getElementById('guide-modal-content');
  const guideModalClose = document.getElementById('guide-modal-close');

  const taskGuideHtml = `
    <p class="guide-intro">
      下記の1から16までは，実行すると記述してあるような結果になる関数がある。
      この結果になるときどのような動作をするか考えて，それらを日本語で説明しなさい。
      また，17についても実行例についてどのように動作しているのか，日本語で説明しなさい。
      18から20は説明に対する動作例を自分で考え，そのときの動作を日本語で説明しなさい。
      また，各問いに対するOCaml定義を行い，ソースコードを作成しなさい。
      すべてのソースコードは一つのファイルにまとめること。
    </p>

    <h3 class="guide-section-title">1〜16. 実行例から動作を説明する関数</h3>

    <ul class="guide-list">
      <li class="guide-card">
        <p class="guide-card-title">1. checkl</p>
        <p class="guide-card-text">指定した値がリストの中に含まれているかを判定する関数。</p>
        <pre class="guide-card-code"># checkl;;
  - : 'a -> 'a list -> bool = &lt;fun&gt;
  # checkl 3 [1; 2; 3; 4; 5; 6];;
  - : bool = true
  # checkl 1 [2; 3; 4; 5];;
  - : bool = false</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">2. dellt</p>
        <p class="guide-card-text">指定した位置以降のリストを返す関数。負の値の場合は例外を発生させる。</p>
        <pre class="guide-card-code"># dellt;;
  - : int -> 'a list -> 'a list = &lt;fun&gt;
  # dellt 0 [1;2;3;4];;
  - : int list = [1; 2; 3; 4]
  # dellt 1 [1;2;3;4];;
  - : int list = [2; 3; 4]
  # dellt 2 [1;2;3;4];;
  - : int list = [3; 4]
  # dellt 3 [1;2;3;4];;
  - : int list = [4]
  # dellt 5 [1;2;3;4];;
  - : int list = []
  # dellt 3 ["A"; "B"; "C"; "D"; "E"; "F"];;
  - : string list = ["D"; "E"; "F"]
  # dellt(-2) [1; 2];;
  Exception: Failure "Error".</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">3. dellt2</p>
        <p class="guide-card-text">指定した位置の要素だけをリストから取り除く関数。</p>
        <pre class="guide-card-code"># dellt2;;
  - : int -> 'a list -> 'a list = &lt;fun&gt;
  # dellt2 1 ["A"; "B"; "C"; "D"; "E"; "F"];;
  - : string list = ["B"; "C"; "D"; "E"; "F"]
  # dellt2 3 ["A"; "B"; "C"; "D"; "E"; "F"];;
  - : string list = ["A"; "B"; "D"; "E"; "F"]
  # dellt2 3 [1; 2; 3; 4; 5; 6];;
  - : int list = [1; 2; 4; 5; 6]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">4. posl</p>
        <p class="guide-card-text">指定した位置の要素を取り出す関数。存在しない位置の場合は例外を発生させる。</p>
        <pre class="guide-card-code"># posl;;
  - : int -> 'a list -> 'a = &lt;fun&gt;
  # posl 3 ["AB"; "C"; "DEF"; "G"; "H"; "IJ"];;
  - : string = "DEF"
  # posl 2 [ 1; 2; 3; 4; 5];;
  - : int = 2
  # posl 0 [ 1; 2; 3; 4; 5];;
  Exception: Failure "Not Exist...".</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">5. add2list</p>
        <p class="guide-card-text">隣り合う要素同士を足し合わせた結果をリストとして返す関数。</p>
        <pre class="guide-card-code"># add2list;;
  - : int list -> int list = &lt;fun&gt;
  # add2list [1; 2];;
  - : int list = [3]
  # add2list [1; 2; 3];;
  - : int list = [3; 5]
  # add2list [1; 2; 3; 4; 5];;
  - : int list = [3; 5; 7; 9]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">6. mullist</p>
        <p class="guide-card-text">2つのリストの同じ位置にある要素同士を掛け合わせたリストを返す関数。</p>
        <pre class="guide-card-code"># mullist;;
  - : int list -> int list -> int list = &lt;fun&gt;
  # mullist [1; 3; 5; 7] [2; 4; 6; 8];;
  - : int list = [2; 12; 30; 56]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">7. chglist</p>
        <p class="guide-card-text">リスト内の指定した値を，別の値に置き換える関数。</p>
        <pre class="guide-card-code"># chglist;;
  - : 'a * 'a -> 'a list -> 'a list = &lt;fun&gt;
  # chglist ("A", "*") ["1"; "A"; "2"; "B"; "A"; "A"; "3"; "4"];;
  - : string list = ["1"; "*"; "2"; "B"; "*"; "*"; "3"; "4"]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">8. replicate</p>
        <p class="guide-card-text">指定した値を指定回数だけ繰り返したリストを作る関数。</p>
        <pre class="guide-card-code"># replicate;;
  - : int -> 'a -> 'a list = &lt;fun&gt;
  # replicate 3 ["A"];;
  - : string list list = [["A"]; ["A"]; ["A"]]
  # replicate 5 "A";;
  - : string list = ["A"; "A"; "A"; "A"; "A"]
  # replicate 3 ["1"; "#"];;
  - : string list list = [["1"; "#"]; ["1"; "#"]; ["1"; "#"]]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">9. inslist</p>
        <p class="guide-card-text">指定した位置に要素を挿入する関数。位置が0の場合は例外を発生させる。</p>
        <pre class="guide-card-code"># inslist;;
  - : int -> 'a -> 'a list -> 'a list = &lt;fun&gt;
  # inslist 2 "*" ["A"; "B"; "C"; "D"; "E"];;
  - : string list = ["A"; "*"; "B"; "C"; "D"; "E"]
  # inslist 6 "*" ["A"; "B"; "C"; "D"; "E"];;
  - : string list = ["A"; "B"; "C"; "D"; "E"; "*"]
  # inslist 1 "+" [];;
  - : string list = ["+"]
  # inslist 1 "+" ["A"];;
  - : string list = ["+"; "A"]
  # inslist 0 "+" ["A"];;
  Exception: Failure "Error".</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">10. merge</p>
        <p class="guide-card-text">2つのリストの要素を交互に並べたリストを返す関数。</p>
        <pre class="guide-card-code"># merge;;
  - : 'a list -> 'a list -> 'a list = &lt;fun&gt;
  # merge [1; 2; 3] [4; 5; 6];;
  - : int list = [1; 4; 2; 5; 3; 6]
  # merge ["A"; "B"] [ "C"; "D"; "EF"; "GH"];;
  - : string list = ["A"; "C"; "B"; "D"; "EF"; "GH"]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">11. inside_length</p>
        <p class="guide-card-text">リストの中にある各リストの要素数を合計して返す関数。</p>
        <pre class="guide-card-code"># inside_length;;
  - : 'a list list -> int = &lt;fun&gt;
  # inside_length[[1; 2; 3]; [4; 5]; [6]; [7; 8; 9; 10]];;
  - : int = 10
  # inside_length[["A"; "B"]; [ "C"; "D"]; ["EF"; "GH"]];;
  - : int = 6</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">12. concat</p>
        <p class="guide-card-text">リストの中にある複数のリストを，1つのリストにつなげる関数。</p>
        <pre class="guide-card-code"># concat;;
  - : 'a list list -> 'a list = &lt;fun&gt;
  # concat [[0; 3; 4]; [2]; [0]; [5; 0]];;
  - : int list = [0; 3; 4; 2; 0; 5; 0]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">13. assoc</p>
        <p class="guide-card-text">ペアのリストから，指定した値と対応する値を探して返す関数。</p>
        <pre class="guide-card-code"># assoc;;
  - : 'a -> ('a * 'a) list -> 'a = &lt;fun&gt;
  # assoc 33 [(3,4); (33,5); (11,2); (55,1)];;
  - : int = 5
  # assoc 2 [(3,4); (33,5); (11,2); (55,1)];;
  - : int = 11
  # assoc "03" [("Kyoto", "075"); ("Osaka", "06"); ("Tokyo", "03")];;
  - : string = "Tokyo"
  # assoc "Kyoto" [("Kyoto", "075"); ("Osaka", "06"); ("Tokyo", "03")];;
  - : string = "075"
  # assoc 6 [(3,4); (33,5); (11,2); (55,1)];;
  Exception: Failure "Not found...".</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">14. minimum</p>
        <p class="guide-card-text">リストの中で最小の要素を返す関数。空リストの場合は例外を発生させる。</p>
        <pre class="guide-card-code"># minimum;;
  - : 'a list -> 'a = &lt;fun&gt;
  # minimum [3; 2; 5; 1];;
  - : int = 1
  # minimum ["abc"; "sdf"];;
  - : string = "abc"
  # minimum [];;
  Exception: Failure "Error".</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">15. extract</p>
        <p class="guide-card-text">条件を満たす要素だけを取り出したリストを返す関数。</p>
        <pre class="guide-card-code"># extract;;
  - : ('a -> bool) -> 'a list -> 'a list = &lt;fun&gt;
  # extract (fun x -> x > 10) [21; 2; 31; 1];;
  - : int list = [21; 31]</pre>
      </li>

      <li class="guide-card">
        <p class="guide-card-title">16. index</p>
        <p class="guide-card-text">指定した要素がリストの何番目にあるかを返す関数。先頭は0番目として数える。</p>
        <pre class="guide-card-code"># index;;
  - : 'a list -> 'a -> int = &lt;fun&gt;
  # index [21; 2; 31; 1] 21;;
  - : int = 0
  # index ['a'; '3'; 'b'; 'z'; '1'] 'z';;
  - : int = 3</pre>
      </li>
    </ul>

    <h3 class="guide-section-title">17. 経路数 numOfRotes</h3>

    <div class="guide-card">
      <p class="guide-card-title">17. 経路数: numOfRotes</p>
      <p class="guide-card-text">
        碁盤目状の道路がある。始点から終点までの経路の数を求める。
        ただし，始点から終点までの経路は最短経路のみとする。
        すなわち，進行方向は右方向または上方向に限られ，左方向または下方向に進むことはできない。
      </p>
      <div class="guide-image-wrap">
        <img class="guide-image" src="/task17_routes.png" alt="numOfRotes の経路図">
      </div>
      <pre class="guide-card-code"># numOfRotes;;
  - : int * int -> int = &lt;fun&gt;
  # numOfRotes (5, 4);;
  - : int = 126</pre>
    </div>

    <h3 class="guide-section-title">18〜20. 集合の計算</h3>

    <div class="guide-card">
      <p class="guide-card-title">集合の計算</p>
      <p class="guide-card-text">
        リストを集合と見なして，以下の集合計算をする関数を定義する。
        ただし，各集合では同じ要素の重複は許されない。
      </p>

      <div class="guide-subitems">
        <div class="guide-subitem">
          <p class="guide-card-title">18. inter</p>
          <p class="guide-card-text">二つの集合の積，共通要素を返す関数。</p>
        </div>

        <div class="guide-subitem">
          <p class="guide-card-title">19. union</p>
          <p class="guide-card-text">二つの集合の和を返す関数。</p>
        </div>

        <div class="guide-subitem">
          <p class="guide-card-title">20. diff</p>
          <p class="guide-card-text">二つの集合の差を返す関数。</p>
        </div>
      </div>
    </div>

    <h3 class="guide-section-title">課題提出</h3>

    <div class="guide-card">
      <p class="guide-card-title">提出方法</p>
      <ul class="guide-submit-list">
        <li>提出期限: 2026/5/13（水）13:00</li>
        <li>提出方法: LETUSにて提出</li>
        <li>提出物: レポート（LaTeXで作成したPDF）と，プログラムソースコード（拡張子ml）</li>
        <li>PDFおよびmlファイルは，それぞれ一つのファイルにまとめること</li>
        <li>実行例と同じ結果が出る関数を定義する</li>
        <li>18，19，20は自分で実行例を作成する</li>
        <li>実行例が表示される関数呼び出しもソースコード内に含めること</li>
        <li>Exceptionが出る呼び出しは，プログラムの動作が止まってしまうのでコメントアウトしておくこと</li>
        <li>今回の課題は考察不要</li>
      </ul>
    </div>
  `;

  const criteriaGuideHtml = `
    <div class="guide-card">
      <p class="guide-card-title">採点の基本方針</p>
      <p class="guide-card-text">
        基本的には，プログラムだけで点数をつけてください。
        課題ページと同じ動作をすれば満点です。
      </p>

      <div class="guide-subitems">
        <div class="guide-subitem">
          <p class="guide-card-title">点数配分</p>
          <ul class="guide-submit-list">
            <li>各問題10点</li>
            <li>合計200点満点</li>
          </ul>
        </div>

        <div class="guide-subitem">
          <p class="guide-card-title">採点基準</p>
          <ul class="guide-submit-list">
            <li>課題ページに書かれている動作をするプログラムの場合：10点</li>
            <li>警告が出る：9点</li>
            <li>プログラムが課題どおり動かない場合：動作の説明が適切な場合：5点</li>
          </ul>
        </div>
      </div>
    </div>
  `;

  function openGuideMenu() {
    if (!guideMenuWrap) {
      return;
    }

    guideMenuWrap.classList.toggle('open');
  }

  function closeGuideMenu() {
    if (!guideMenuWrap) {
      return;
    }

    guideMenuWrap.classList.remove('open');
  }

  function openGuideModal(type) {
    if (!guideModalOverlay || !guideModalTitle || !guideModalContent) {
      return;
    }

    if (type === 'tasks') {
      guideModalTitle.textContent = '課題内容';
      guideModalContent.innerHTML = taskGuideHtml;
    } else {
      guideModalTitle.textContent = '採点基準';
      guideModalContent.innerHTML = criteriaGuideHtml;
    }

    guideModalContent.querySelectorAll('.guide-card-code').forEach(function (codeBlock) {
      codeBlock.textContent = codeBlock.textContent
        .split('\\n')
        .map(function (line) {
          return line.replace(/^\\s+/, '');
        })
        .join('\\n')
        .trim();
    });

    closeGuideMenu();
    guideModalOverlay.classList.add('show');
    guideModalOverlay.setAttribute('aria-hidden', 'false');
  }

  function closeGuideModal() {
    if (!guideModalOverlay || !guideModalTitle || !guideModalContent) {
      return;
    }

    guideModalOverlay.classList.remove('show');
    guideModalOverlay.setAttribute('aria-hidden', 'true');

    setTimeout(function () {
      if (!guideModalOverlay.classList.contains('show')) {
        guideModalTitle.textContent = '';
        guideModalContent.innerHTML = '';
      }
    }, 220);
  }

  if (guideMenuButton) {
    guideMenuButton.addEventListener('click', function (e) {
      e.stopPropagation();
      openGuideMenu();
    });
  }

  document.querySelectorAll('.guide-menu-item').forEach(function (button) {
    button.addEventListener('click', function () {
      openGuideModal(button.getAttribute('data-guide'));
    });
  });

  if (guideModalClose) {
    guideModalClose.addEventListener('click', closeGuideModal);
  }

  if (guideModalOverlay) {
    guideModalOverlay.addEventListener('click', function (e) {
      if (e.target === guideModalOverlay) {
        closeGuideModal();
      }
    });
  }

  document.addEventListener('click', function (e) {
    if (guideMenuWrap && !guideMenuWrap.contains(e.target)) {
      closeGuideMenu();
    }
  });

  const uploadForm = document.getElementById('upload-form');
  const loadingOverlay = document.getElementById('loading-overlay');
  const fileInput = document.getElementById('file-input');
  const resultFrameOverlay = document.getElementById('result-frame-overlay');
  const resultFrame = document.getElementById('result-frame');
  let isSubmittingToFrame = false;
  const fileDrop = document.querySelector('.file-drop');
  const selectedFiles = document.getElementById('selected-files');
  const selectedFileList = document.getElementById('selected-file-list');
  const clearFilesButton = document.getElementById('clear-files-button');

  const bulkModeButton = document.getElementById('bulk-mode-button');
  const studentModeButton = document.getElementById('student-mode-button');
  const uploadModeInput = document.getElementById('upload-mode-input');
  const bulkUploadPanel = document.getElementById('bulk-upload-panel');
  const studentUploadPanel = document.getElementById('student-upload-panel');
  const studentUploadRows = document.getElementById('student-upload-rows');
  const addStudentRowButton = document.getElementById('add-student-row-button');

  const deleteModalOverlay = document.getElementById('delete-modal-overlay');
  const deleteModalTitle = document.getElementById('delete-modal-title');
  const deleteModalText = document.getElementById('delete-modal-text');
  const deleteCancelButton = document.getElementById('delete-cancel-button');
  const deleteConfirmButton = document.getElementById('delete-confirm-button');

  let deleteTargetKey = null;
  let deleteMode = null;
  let selectedFileStore = [];

  function fileKey(file) {
    return file.name + '|' + file.size + '|' + file.lastModified;
  }

  function syncFileInput() {
    const dataTransfer = new DataTransfer();

    selectedFileStore.forEach(function (file) {
      dataTransfer.items.add(file);
    });

    fileInput.files = dataTransfer.files;
  }

  function addFiles(filesToAdd) {
    const incomingFiles = Array.from(filesToAdd || []).filter(function (file) {
      return file.name.toLowerCase().endsWith('.ml');
    });

    if (incomingFiles.length === 0) {
      return;
    }

    const seen = new Set(selectedFileStore.map(fileKey));

    incomingFiles.forEach(function (file) {
      const key = fileKey(file);

      if (seen.has(key)) {
        return;
      }

      seen.add(key);
      selectedFileStore.push(file);
    });

    syncFileInput();
    updateSelectedFiles();
  }

  function updateSelectedFiles() {
    selectedFileList.innerHTML = '';

    if (selectedFileStore.length === 0) {
      selectedFiles.classList.add('is-empty');
      clearFilesButton.classList.remove('show');

      const emptyItem = document.createElement('li');
      emptyItem.textContent = 'まだファイルが選択されていません。';
      selectedFileList.appendChild(emptyItem);
      return;
    }

    selectedFiles.classList.remove('is-empty');
    clearFilesButton.classList.add('show');

    selectedFileStore.forEach(function (file) {
      const item = document.createElement('li');
      item.className = 'selected-file-item';
      item.textContent = file.name;
      item.setAttribute('tabindex', '0');
      item.setAttribute('role', 'button');
      item.setAttribute('aria-label', file.name + ' を削除');

      item.addEventListener('click', function () {
        openDeleteModal(file);
      });

      item.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openDeleteModal(file);
        }
      });

      selectedFileList.appendChild(item);
    });
  }

  function setUploadMode(mode) {
    const isBulk = mode === 'bulk';

    uploadModeInput.value = mode;

    bulkModeButton.classList.toggle('active', isBulk);
    studentModeButton.classList.toggle('active', !isBulk);

    bulkUploadPanel.hidden = !isBulk;
    studentUploadPanel.hidden = isBulk;

    if (!isBulk) {
      fileInput.disabled = true;
    } else {
      fileInput.disabled = false;
    }
  }

  let isStudentSorting = false;
  let sortingStudentRow = null;
  let sortingPointerId = null;
  let pendingSortRow = null;
  let pendingLongPressTimer = null;
  let pointerStartX = 0;
  let pointerStartY = 0;
  let studentDragGhost = null;
  let studentDragGhostOffsetX = 0;
  let studentDragGhostOffsetY = 0;
  let studentSortPlaceholder = null;
  let isStudentSortDropping = false;
  let isStudentDeleteReady = false;
  let studentDeleteThresholdX = 96;
  let studentDeleteHintX = 32;
  let pendingDeleteStudentRow = null;
  let pendingDeleteStudentPlaceholder = null;
  let studentDragMode = null;

  function clearStudentSortTargets() {
    document.querySelectorAll('.student-upload-row').forEach(function (row) {
      row.classList.remove('is-sort-target-before');
      row.classList.remove('is-sort-target-after');
    });
  }

  function getStudentRowInsertPosition(pointerY) {
    const rows = Array.from(studentUploadRows.querySelectorAll('.student-upload-row'))
      .filter(function (row) {
        return row !== sortingStudentRow;
      });

    for (const row of rows) {
      const box = row.getBoundingClientRect();
      const middleY = box.top + box.height / 2;

      if (pointerY < middleY) {
        return {
          row: row,
          position: 'before'
        };
      }
    }

    if (rows.length > 0) {
      return {
        row: rows[rows.length - 1],
        position: 'after'
      };
    }

    return {
      row: null,
      position: 'after'
    };
  }

  function createStudentDragGhost(row) {
    const box = row.getBoundingClientRect();

    studentDragGhost = row.cloneNode(true);

    studentDragGhost.classList.remove('is-sorting');
    studentDragGhost.classList.remove('is-sort-ready');
    studentDragGhost.classList.remove('is-ghost-source');
    studentDragGhost.classList.remove('is-dragging-file');
    studentDragGhost.classList.remove('is-invalid-file');

    studentDragGhost.classList.add('student-drag-ghost');
    studentDragGhost.classList.add('student-drag-ghost-pickup');

    studentDragGhost.style.width = box.width + 'px';
    studentDragGhost.style.height = box.height + 'px';
    studentDragGhost.style.left = box.left + 'px';
    studentDragGhost.style.top = box.top + 'px';

    studentDragGhostOffsetX = pointerStartX - box.left;
    studentDragGhostOffsetY = pointerStartY - box.top;

    document.body.appendChild(studentDragGhost);

    setTimeout(function () {
      if (studentDragGhost) {
        studentDragGhost.classList.remove('student-drag-ghost-pickup');
      }
    }, 180);
  }

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function rubberHorizontalMove(moveX, moveY) {
    if (studentDragMode === 'delete') {
      return clamp(moveX, -160, 0);
    }

    return 0;
  }

  function moveStudentDragGhost(clientX, clientY) {
    if (!studentDragGhost) {
      return;
    }

    const baseX = pointerStartX - studentDragGhostOffsetX;
    const baseY = pointerStartY - studentDragGhostOffsetY;
    const currentX = clientX - studentDragGhostOffsetX;
    const currentY = clientY - studentDragGhostOffsetY;

    const moveX = currentX - baseX;
    const moveY = currentY - baseY;
    const limitedMoveX = rubberHorizontalMove(moveX, moveY);

    const listBox = studentUploadRows.getBoundingClientRect();
    const ghostBox = studentDragGhost.getBoundingClientRect();

    const topLimit = listBox.top - 24;
    const bottomLimit = listBox.bottom - ghostBox.height + 24;

    const limitedY = clamp(currentY, topLimit, bottomLimit);

    studentDragGhost.style.left = (baseX + limitedMoveX) + 'px';

    if (studentDragMode === 'delete') {
      studentDragGhost.style.top = baseY + 'px';
    } else {
      studentDragGhost.style.top = limitedY + 'px';
    }
  }

  function removeStudentDragGhost() {
    if (studentDragGhost) {
      studentDragGhost.remove();
      studentDragGhost = null;
    }

    studentDragGhostOffsetX = 0;
    studentDragGhostOffsetY = 0;
  }

  function createStudentSortPlaceholder(row) {
    const box = row.getBoundingClientRect();

    studentSortPlaceholder = document.createElement('div');
    studentSortPlaceholder.className = 'student-sort-placeholder';
    studentSortPlaceholder.style.height = box.height + 'px';

    studentUploadRows.insertBefore(studentSortPlaceholder, row);
  }

  function removeStudentSortPlaceholder() {
    if (studentSortPlaceholder) {
      studentSortPlaceholder.remove();
      studentSortPlaceholder = null;
    }
  }

  function setStudentDeleteSlideArea(isVisible, progress) {
    if (!studentSortPlaceholder) {
      return;
    }

    const safeProgress = clamp(progress || 0, 0, 1);

    studentSortPlaceholder.classList.toggle('has-delete-slide-area', isVisible);
    studentSortPlaceholder.style.setProperty('--delete-progress', safeProgress.toFixed(3));

    let area = studentSortPlaceholder.querySelector('.student-delete-slide-area');

    if (isVisible && !area) {
      area = document.createElement('div');
      area.className = 'student-delete-slide-area';
      studentSortPlaceholder.appendChild(area);
    }

    if (area) {
      area.style.setProperty('--delete-progress', safeProgress.toFixed(3));
    }

    if (!isVisible && area) {
      area.remove();
      studentSortPlaceholder.style.removeProperty('--delete-progress');
    }
  }

  function setStudentDeleteReady(isReady) {
    isStudentDeleteReady = isReady;

    if (studentDragGhost) {
      studentDragGhost.classList.toggle('is-delete-ready', isReady);
    }
  }

  function updateStudentDeleteState(clientX, clientY) {
    const moveX = clientX - pointerStartX;
    const moveY = clientY - pointerStartY;

    const absX = Math.abs(moveX);
    const absY = Math.abs(moveY);
    const leftDistance = Math.max(0, -moveX);

    const isMostlyHorizontal = absX > absY * 1.15;
    const isMostlyVertical = absY > absX * 1.15;

    if (studentDragMode === null) {
      if (leftDistance > studentDeleteHintX && isMostlyHorizontal) {
        studentDragMode = 'delete';
      } else if (absY > 18 && isMostlyVertical) {
        studentDragMode = 'sort';
      }
    }

    if (studentDragMode === 'sort') {
      setStudentDeleteSlideArea(false);
      setStudentDeleteReady(false);
      return;
    }

    if (studentDragMode === 'delete') {
      const deleteProgress = clamp(
        (leftDistance - studentDeleteHintX) / (studentDeleteThresholdX - studentDeleteHintX),
        0,
        1
      );

      const isBackToOriginal = moveX > -studentDeleteHintX;

      if (isBackToOriginal) {
        studentDragMode = null;
        setStudentDeleteSlideArea(false);
        setStudentDeleteReady(false);
        return;
      }

      setStudentDeleteSlideArea(true, deleteProgress);
      setStudentDeleteReady(leftDistance > studentDeleteThresholdX);
      return;
    }

    setStudentDeleteSlideArea(false);
    setStudentDeleteReady(false);
  }

  function playStudentRowLanding(row) {
    if (!row) {
      return;
    }

    row.classList.remove('is-drop-landed');
    void row.offsetWidth;
    row.classList.add('is-drop-landed');

    setTimeout(function () {
      row.classList.remove('is-drop-landed');
    }, 260);
  }

  function startStudentSorting(row, pointerId) {
    isStudentSorting = true;
    isStudentSortDropping = false;
    isStudentDeleteReady = false;
    studentDragMode = null;
    pendingDeleteStudentRow = null;
    pendingDeleteStudentPlaceholder = null;
    sortingStudentRow = row;
    sortingPointerId = pointerId;

    row.classList.remove('is-dragging-file');
    row.classList.remove('is-sort-ready');
    row.classList.add('is-sorting');

    createStudentDragGhost(row);
    createStudentSortPlaceholder(row);

    row.remove();

    document.body.classList.add('student-sorting-active');
  }

  function stopStudentSorting() {
    if (isStudentSortDropping) {
      return;
    }

    if (isStudentDeleteReady) {
      const rowToRestore = sortingStudentRow;
      const placeholder = studentSortPlaceholder;

      if (shouldRestoreOnlyEmptyStudentRow(rowToRestore)) {
        setStudentDeleteSlideArea(false);
        setStudentDeleteReady(false);
        studentDragMode = null;
        /*
          return しない。
          このまま下の通常のドロップ処理へ進ませることで、
          ゴーストカードがプレースホルダー位置へスッと戻る。
        */
      } else {
        removeStudentDragGhost();
        setStudentDeleteSlideArea(false);
        setStudentDeleteReady(false);

        if (rowToRestore) {
          rowToRestore.classList.remove('is-sorting');
          rowToRestore.classList.remove('is-sort-ready');
          rowToRestore.classList.remove('is-ghost-source');
        }

        openStudentRowDeleteModal(rowToRestore, placeholder);

        isStudentSorting = false;
        isStudentSortDropping = false;
        isStudentDeleteReady = false;
        studentDragMode = null;
        sortingStudentRow = null;
        sortingPointerId = null;
        pendingSortRow = null;

        document.body.classList.remove('student-sorting-active');
        return;
      }
    }

    isStudentSortDropping = true;
    clearStudentSortTargets();

    if (pendingLongPressTimer) {
      clearTimeout(pendingLongPressTimer);
      pendingLongPressTimer = null;
    }

    if (pendingSortRow) {
      pendingSortRow.classList.remove('is-sort-ready');
    }

    const rowToRestore = sortingStudentRow;
    const placeholder = studentSortPlaceholder;
    const ghost = studentDragGhost;

    function finishStudentSorting() {
      if (rowToRestore) {
        rowToRestore.classList.remove('is-sorting');
        rowToRestore.classList.remove('is-sort-ready');
        rowToRestore.classList.remove('is-ghost-source');

        if (placeholder && placeholder.parentNode === studentUploadRows) {
          studentUploadRows.insertBefore(rowToRestore, placeholder);
        } else {
          studentUploadRows.appendChild(rowToRestore);
        }

        playStudentRowLanding(rowToRestore);
      }
      setStudentDeleteSlideArea(false);
      setStudentDeleteReady(false);

      removeStudentSortPlaceholder();
      removeStudentDragGhost();

      isStudentSorting = false;
      isStudentSortDropping = false;
      isStudentDeleteReady = false;
      studentDragMode = null;
      sortingStudentRow = null;
      sortingPointerId = null;
      pendingSortRow = null;

      document.body.classList.remove('student-sorting-active');
    }

    if (!rowToRestore || !placeholder || !ghost) {
      finishStudentSorting();
      return;
    }

    const targetBox = placeholder.getBoundingClientRect();

    ghost.classList.add('is-dropping');
    ghost.style.left = targetBox.left + 'px';
    ghost.style.top = targetBox.top + 'px';
    ghost.style.width = targetBox.width + 'px';
    ghost.style.height = targetBox.height + 'px';

    let finished = false;

    function handleDropAnimationEnd() {
      if (finished) {
        return;
      }

      finished = true;
      ghost.removeEventListener('transitionend', handleDropAnimationEnd);
      finishStudentSorting();
    }

    ghost.addEventListener('transitionend', handleDropAnimationEnd);

    setTimeout(handleDropAnimationEnd, 260);
  }

  function getStudentSortItems() {
    return Array.from(studentUploadRows.children).filter(function (item) {
      return (
        item.classList.contains('student-upload-row') ||
        item.classList.contains('student-sort-placeholder')
      );
    });
  }

  function animateStudentListChange(changeFn) {
    const firstPositions = new Map();

    getStudentSortItems().forEach(function (item) {
      firstPositions.set(item, item.getBoundingClientRect());
    });

    changeFn();

    getStudentSortItems().forEach(function (item) {
      const firstBox = firstPositions.get(item);

      if (!firstBox) {
        return;
      }

      const lastBox = item.getBoundingClientRect();
      const deltaY = firstBox.top - lastBox.top;

      if (Math.abs(deltaY) < 1) {
        return;
      }

      item.classList.remove('is-list-moving');
      item.style.transition = 'none';
      item.style.transform = 'translate3d(0, ' + deltaY + 'px, 0)';

      item.getBoundingClientRect();

      requestAnimationFrame(function () {
        item.classList.add('is-list-moving');
        item.style.transition = '';
        item.style.transform = '';
      });

      setTimeout(function () {
        item.classList.remove('is-list-moving');
        item.style.transition = '';
        item.style.transform = '';
      }, 240);
    });
  }

  function moveSortingStudentRow(pointerY) {
    if (!isStudentSorting || !studentSortPlaceholder) {
      return;
    }

    const insertPosition = getStudentRowInsertPosition(pointerY);

    clearStudentSortTargets();

    if (insertPosition.row && insertPosition.position === 'before') {
      if (studentSortPlaceholder.nextSibling === insertPosition.row) {
        return;
      }

      animateStudentListChange(function () {
        studentUploadRows.insertBefore(studentSortPlaceholder, insertPosition.row);
      });

      return;
    }

    if (studentUploadRows.lastElementChild === studentSortPlaceholder) {
      return;
    }

    animateStudentListChange(function () {
      studentUploadRows.appendChild(studentSortPlaceholder);
    });
  }

  document.addEventListener('pointermove', function (e) {
    if (sortingPointerId !== null && e.pointerId !== sortingPointerId) {
      return;
    }

    if (pendingSortRow && !isStudentSorting) {
      const moveX = Math.abs(e.clientX - pointerStartX);
      const moveY = Math.abs(e.clientY - pointerStartY);

      if (moveX > 8 || moveY > 8) {
        if (pendingLongPressTimer) {
          clearTimeout(pendingLongPressTimer);
          pendingLongPressTimer = null;
        }

        pendingSortRow.classList.remove('is-sort-ready');
        pendingSortRow = null;
        sortingPointerId = null;
      }

      return;
    }

    if (!isStudentSorting || isStudentSortDropping) {
      return;
    }

    e.preventDefault();

    moveStudentDragGhost(e.clientX, e.clientY);
    updateStudentDeleteState(e.clientX, e.clientY);

    if (studentDragMode !== 'delete') {
      moveSortingStudentRow(e.clientY);
    }
  });

  document.addEventListener('pointerup', function (e) {
    if (sortingPointerId !== null && e.pointerId !== sortingPointerId) {
      return;
    }

    stopStudentSorting();
  });

  document.addEventListener('pointercancel', function (e) {
    if (sortingPointerId !== null && e.pointerId !== sortingPointerId) {
      return;
    }

    stopStudentSorting();
  });

  function addStudentRow(studentIdValue) {
    const row = document.createElement('div');
    row.className = 'student-upload-row';

    const studentInput = document.createElement('input');
    studentInput.className = 'student-id-input';
    studentInput.type = 'text';
    studentInput.name = 'student_ids';
    studentInput.placeholder = '例：6325000';
    studentInput.value = studentIdValue || '';

    const fileInput = document.createElement('input');
    fileInput.className = 'student-file-input';
    fileInput.type = 'file';
    fileInput.name = 'student_files';
    fileInput.accept = '.ml';

    const fileControl = document.createElement('div');
    fileControl.className = 'student-file-control';

    const fileNameText = document.createElement('span');
    fileNameText.className = 'student-file-name';
    fileNameText.textContent = 'ファイルが選択されていません';

    function updateStudentFileNameText() {
      if (fileInput.files && fileInput.files[0]) {
        fileNameText.textContent = fileInput.files[0].name;
      } else {
        fileNameText.textContent = 'ファイルが選択されていません';
      }
    }

    fileInput.addEventListener('change', updateStudentFileNameText);

    function setStudentRowFile(file) {
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);

      fileInput.files = dataTransfer.files;

      fileInput.dispatchEvent(new Event('change', { bubbles: true }));
    }

    function getDroppedMlFile(files) {
      const droppedFiles = Array.from(files || []);

      return droppedFiles.find(function (file) {
        return file.name.toLowerCase().endsWith('.ml');
      });
    }

    function showInvalidFileFeedback() {
      row.classList.remove('is-invalid-file');
      void row.offsetWidth;
      row.classList.add('is-invalid-file');

      setTimeout(function () {
        row.classList.remove('is-invalid-file');
      }, 350);
    }

    function isInteractiveTarget(target) {
      return Boolean(target.closest('input, button, label, select, textarea'));
    }

    row.addEventListener('dragenter', function (e) {
      e.preventDefault();
      e.stopPropagation();

      if (isStudentSorting) {
        return;
      }

      row.classList.add('is-dragging-file');
    });

    row.addEventListener('dragover', function (e) {
      e.preventDefault();
      e.stopPropagation();

      if (isStudentSorting) {
        return;
      }

      row.classList.add('is-dragging-file');
    });

    row.addEventListener('dragleave', function (e) {
      e.preventDefault();
      e.stopPropagation();

      if (!row.contains(e.relatedTarget)) {
        row.classList.remove('is-dragging-file');
      }
    });

    row.addEventListener('drop', function (e) {
      e.preventDefault();
      e.stopPropagation();

      row.classList.remove('is-dragging-file');

      if (isStudentSorting) {
        return;
      }

      const mlFile = getDroppedMlFile(e.dataTransfer.files);

      if (!mlFile) {
        showInvalidFileFeedback();
        return;
      }

      setStudentRowFile(mlFile);
    });

    row.addEventListener('pointerdown', function (e) {
      if (e.button !== 0) {
        return;
      }

      if (isInteractiveTarget(e.target)) {
        return;
      }

      if (pendingLongPressTimer) {
        clearTimeout(pendingLongPressTimer);
      }

      pendingSortRow = row;
      sortingPointerId = e.pointerId;
      pointerStartX = e.clientX;
      pointerStartY = e.clientY;

      row.classList.add('is-sort-ready');

      pendingLongPressTimer = setTimeout(function () {
        if (pendingSortRow !== row) {
          return;
        }

        pendingLongPressTimer = null;
        startStudentSorting(row, e.pointerId);
      }, 520);
    });

    fileControl.appendChild(fileInput);
    fileControl.appendChild(fileNameText);

    row.appendChild(studentInput);
    row.appendChild(fileControl);

    studentUploadRows.appendChild(row);
  }

  function getNextStudentId() {
    const rows = Array.from(document.querySelectorAll('.student-upload-row'));

    if (rows.length === 0) {
      return '';
    }

    const lastRow = rows[rows.length - 1];
    const studentInput = lastRow.querySelector('.student-id-input');

    if (!studentInput) {
      return '';
    }

    const value = studentInput.value.trim();

    if (!/^[0-9]+$/.test(value)) {
      return '';
    }

    const nextValue = (BigInt(value) + 1n).toString();

    return nextValue.padStart(value.length, '0');
  }

  function openDeleteModal(file) {
    deleteMode = 'single';
    deleteTargetKey = fileKey(file);

    deleteModalTitle.textContent = 'このファイルを削除しますか？';
    deleteModalText.textContent = file.name;
    deleteConfirmButton.textContent = '削除';

    deleteModalOverlay.classList.add('show');
    deleteModalOverlay.setAttribute('aria-hidden', 'false');
  }

  function getStudentRowDeleteLabel(row) {
    if (!row) {
      return 'この行';
    }

    const studentInput = row.querySelector('.student-id-input');
    const fileInput = row.querySelector('.student-file-input');

    const studentId = studentInput ? studentInput.value.trim() : '';
    const fileName = fileInput && fileInput.files && fileInput.files[0]
      ? fileInput.files[0].name
      : 'ファイル未選択';

    if (studentId) {
      return studentId + ' / ' + fileName;
    }

    return fileName;
  }

  function isEmptyStudentRow(row) {
    if (!row) {
      return false;
    }

    const studentInput = row.querySelector('.student-id-input');
    const fileInput = row.querySelector('.student-file-input');

    const studentId = studentInput ? studentInput.value.trim() : '';
    const hasFile = fileInput && fileInput.files && fileInput.files.length > 0;

    return studentId === '' && !hasFile;
  }

  function shouldRestoreOnlyEmptyStudentRow(row) {
    if (!row || !studentUploadRows) {
      return false;
    }

    const rows = Array.from(studentUploadRows.querySelectorAll('.student-upload-row'));
    const rowIsAlreadyInList = rows.indexOf(row) !== -1;

    /*
      並び替え中は startStudentSorting() で対象 row が一度 DOM から remove される。
      そのため、DOM上の行数だけを見ると 0 になってしまう。
      row が DOM から外れている場合は、その1枚を足して数える。
    */
    const totalRows = rows.length + (rowIsAlreadyInList ? 0 : 1);

    return totalRows === 1 && isEmptyStudentRow(row);
  }
  function openStudentRowDeleteModal(row, placeholder) {
    deleteMode = 'student-row';
    deleteTargetKey = null;
    pendingDeleteStudentRow = row;
    pendingDeleteStudentPlaceholder = placeholder;

    deleteModalTitle.textContent = 'このファイルを削除しますか？';
    deleteModalText.textContent = getStudentRowDeleteLabel(row);
    deleteConfirmButton.textContent = '削除';

    deleteModalOverlay.classList.add('show');
    deleteModalOverlay.setAttribute('aria-hidden', 'false');
  }

  function openClearAllModal() {
    if (selectedFileStore.length === 0) {
      return;
    }

    deleteMode = 'all';
    deleteTargetKey = null;

    deleteModalTitle.innerHTML = '選択中のファイルを<br>すべて削除しますか？';
    deleteModalText.textContent = selectedFileStore.length + '件のファイルが選択されています。';
    deleteConfirmButton.textContent = 'すべて削除';

    deleteModalOverlay.classList.add('show');
    deleteModalOverlay.setAttribute('aria-hidden', 'false');
  }

  function restorePendingStudentRowDelete() {
    if (pendingDeleteStudentRow) {
      if (pendingDeleteStudentPlaceholder && pendingDeleteStudentPlaceholder.parentNode === studentUploadRows) {
        studentUploadRows.insertBefore(pendingDeleteStudentRow, pendingDeleteStudentPlaceholder);
      } else {
        studentUploadRows.appendChild(pendingDeleteStudentRow);
      }

      pendingDeleteStudentRow.classList.remove('is-sorting');
      pendingDeleteStudentRow.classList.remove('is-sort-ready');
      pendingDeleteStudentRow.classList.remove('is-ghost-source');

      playStudentRowLanding(pendingDeleteStudentRow);
    }

    if (pendingDeleteStudentPlaceholder) {
      pendingDeleteStudentPlaceholder.remove();
    }

    pendingDeleteStudentRow = null;
    pendingDeleteStudentPlaceholder = null;
    isStudentDeleteReady = false;
    studentDragMode = null;
  }

  function closeDeleteModal() {
    if (deleteMode === 'student-row') {
      restorePendingStudentRowDelete();
    }

    deleteTargetKey = null;
    deleteMode = null;

    deleteModalOverlay.classList.remove('show');
    deleteModalOverlay.setAttribute('aria-hidden', 'true');
  }

  function deleteSelectedFile() {
    if (deleteMode === 'student-row') {
      const placeholderToRemove = pendingDeleteStudentPlaceholder;

      pendingDeleteStudentRow = null;
      pendingDeleteStudentPlaceholder = null;
      isStudentDeleteReady = false;

      deleteTargetKey = null;
      deleteMode = null;

      deleteModalOverlay.classList.remove('show');
      deleteModalOverlay.setAttribute('aria-hidden', 'true');

      if (placeholderToRemove) {
        setTimeout(function () {
          requestAnimationFrame(function () {
            animateStudentListChange(function () {
              placeholderToRemove.remove();
            });

            if (studentUploadRows.children.length === 0) {
              addStudentRow('');
            }
          });
        }, 180);
      } else if (studentUploadRows.children.length === 0) {
        addStudentRow('');
      }

      return;
    }

    if (deleteMode === 'all') {
      selectedFileStore = [];
      syncFileInput();
      updateSelectedFiles();
      closeDeleteModal();
      return;
    }

    if (deleteMode === 'single' && deleteTargetKey) {
      selectedFileStore = selectedFileStore.filter(function (file) {
        return fileKey(file) !== deleteTargetKey;
      });

      syncFileInput();
      updateSelectedFiles();
      closeDeleteModal();
      return;
    }

    closeDeleteModal();
  }

  fileInput.addEventListener('change', function () {
    addFiles(fileInput.files);
  });

  if (fileDrop) {
    fileDrop.addEventListener('dragenter', function (e) {
      e.preventDefault();
      e.stopPropagation();
      fileDrop.classList.add('is-dragging');
    });

    fileDrop.addEventListener('dragover', function (e) {
      e.preventDefault();
      e.stopPropagation();
      fileDrop.classList.add('is-dragging');
    });

    fileDrop.addEventListener('dragleave', function (e) {
      e.preventDefault();
      e.stopPropagation();

      if (!fileDrop.contains(e.relatedTarget)) {
        fileDrop.classList.remove('is-dragging');
      }
    });

    fileDrop.addEventListener('drop', function (e) {
      e.preventDefault();
      e.stopPropagation();

      fileDrop.classList.remove('is-dragging');
      addFiles(e.dataTransfer.files);
    });
  }

  document.addEventListener('drop', function () {
    if (fileDrop) {
      fileDrop.classList.remove('is-dragging');
    }
  });

  document.addEventListener('dragend', function () {
    if (fileDrop) {
      fileDrop.classList.remove('is-dragging');
    }
  });

  deleteCancelButton.addEventListener('click', closeDeleteModal);
  deleteConfirmButton.addEventListener('click', deleteSelectedFile);
  clearFilesButton.addEventListener('click', openClearAllModal);

  bulkModeButton.addEventListener('click', function () {
    setUploadMode('bulk');
  });

  studentModeButton.addEventListener('click', function () {
    setUploadMode('student');
  });

  addStudentRowButton.addEventListener('click', function () {
    addStudentRow(getNextStudentId());
  });

  addStudentRow('');
  setUploadMode('bulk');

  deleteModalOverlay.addEventListener('click', function (e) {
    if (e.target === deleteModalOverlay) {
      closeDeleteModal();
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') {
      return;
    }

    closeGuideMenu();

    if (guideModalOverlay && guideModalOverlay.classList.contains('show')) {
      closeGuideModal();
    }

    if (deleteModalOverlay.classList.contains('show')) {
      closeDeleteModal();
    }
  });

  uploadForm.addEventListener('submit', function (e) {
    if (uploadModeInput.value === 'bulk') {
      syncFileInput();

      if (selectedFileStore.length === 0) {
        e.preventDefault();
        return;
      }
    }

    if (uploadModeInput.value === 'student') {
      const rows = Array.from(document.querySelectorAll('.student-upload-row'));
      const hasValidRow = rows.some(function (row) {
        const studentInput = row.querySelector('.student-id-input');
        const fileInput = row.querySelector('.student-file-input');

        return studentInput && studentInput.value.trim() && fileInput && fileInput.files.length > 0;
      });

      if (!hasValidRow) {
        e.preventDefault();
        return;
      }
    }

    isSubmittingToFrame = true;
    loadingOverlay.classList.add('show');
  });

  resultFrame.addEventListener('load', function () {
    if (!isSubmittingToFrame) {
      return;
    }

    isSubmittingToFrame = false;
    loadingOverlay.classList.remove('show');
    resultFrameOverlay.hidden = false;
    document.body.classList.add('result-frame-open');
  });

  window.addEventListener('message', function (e) {
    if (!e.data || e.data.type !== 'close-result-frame') {
      return;
    }

    resultFrameOverlay.hidden = true;
    resultFrame.src = 'about:blank';
    document.body.classList.remove('result-frame-open');
  });

  updateSelectedFiles();
});
</script>
""")
    html.append("</body>")
    html.append("</html>")

    return "\n".join(html)

def check_uploaded_files(upload_dir, file_metadata=None, checker_module=run_checker):
    all_results = []
    file_summaries = []
    file_metadata = file_metadata or {}

    def file_order(path):
        metadata = file_metadata.get(path.name, {})
        return (
            metadata.get("order", 10**9),
            path.name
        )

    ml_files = sorted(upload_dir.glob("*.ml"), key=file_order)

    for ml_file in ml_files:
        file_results = []

        # まずは54個の小テストをすべて実行する
        for test in checker_module.TESTS:
            result = checker_module.run_one_test(ml_file, test)
            all_results.append(result)
            file_results.append(result)

        # 小テスト結果を1〜20の大問単位にまとめる
        question_summaries = checker_module.summarize_by_question(file_results)

        question_ok_count = 0
        question_warning_count = 0
        question_ng_count = 0
        question_error_count = 0

        for summary in question_summaries:
            if summary["status"] == "OK":
                question_ok_count += 1
            elif summary["status"] == "WARNING":
                question_warning_count += 1
            elif summary["status"] == "NG":
                question_ng_count += 1
            else:
                question_error_count += 1

        question_total = (
            question_ok_count
            + question_warning_count
            + question_ng_count
            + question_error_count
        )

        metadata = file_metadata.get(ml_file.name, {})

        file_summaries.append({
            "file": metadata.get("original_filename", ml_file.name),
            "student_id": metadata.get("student_id", ""),
            "ok": question_ok_count,
            "warning": question_warning_count,
            "ng": question_ng_count,
            "error": question_error_count,
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
        elif self.path == "/term" or self.path.startswith("/term?"):
            self.send_html(build_term_select_html())
        elif self.path == "/period" or self.path.startswith("/period?"):
            self.send_html(build_period_select_html())
        elif self.path == "/period/2" or self.path.startswith("/period/2?"):
            self.send_html(second_period_pages.build_week_select_html(build_carousel_select_html))
        elif self.path == "/period/2/week1" or self.path.startswith("/period/2/week1?"):
            self.send_html(second_period_week1_app.build_index_html())
        elif self.path == "/period/2/week2" or self.path.startswith("/period/2/week2?"):
            self.send_html(second_period_week2_app.build_index_html())
        elif self.path == "/period/2/week3" or self.path.startswith("/period/2/week3?"):
            self.send_html(second_period_week3_app.build_index_html())
        elif self.path == "/upload" or self.path.startswith("/upload?"):
            self.send_html(build_index_html())
        elif self.path == "/background.png":
            self.send_png(BACKGROUND_IMAGE)
        elif self.path == "/task17_routes.png":
            self.send_png(TASK17_IMAGE)
        elif self.path == "/week2_diff_forward_formula.png":
            self.send_png(WEEK2_DIFF_FORWARD_IMAGE)
        elif self.path == "/week2_diff_central_formula.png":
            self.send_png(WEEK2_DIFF_CENTRAL_IMAGE)
        elif self.path == "/week3_answer_table1.png":
            self.send_png(WEEK3_ANSWER_TABLE1_IMAGE)
        elif self.path == "/week3_answer_table2.png":
            self.send_png(WEEK3_ANSWER_TABLE2_IMAGE)
        else:
            self.send_html(build_index_html("ページが見つかりません。"), status=404)

    def do_POST(self):
        if self.path not in ("/check", "/period/2/week1/check", "/period/2/week2/check", "/period/2/week3/check"):
            self.send_html(build_index_html("不正なURLです。"), status=404)
            return

        temp_dir = None

        if self.path == "/period/2/week1/check":
            index_html_builder = second_period_week1_app.build_index_html
            result_html_builder = second_period_week1_app.build_result_html
            checker_module = second_period_week1_checker
        elif self.path == "/period/2/week2/check":
            index_html_builder = second_period_week2_app.build_index_html
            result_html_builder = second_period_week2_app.build_result_html
            checker_module = second_period_week2_checker
        elif self.path == "/period/2/week3/check":
            index_html_builder = second_period_week3_app.build_index_html
            result_html_builder = second_period_week3_app.build_result_html
            checker_module = second_period_week3_checker
        else:
            index_html_builder = build_index_html
            result_html_builder = build_result_html
            checker_module = run_checker

        try:
            content_type = self.headers.get("Content-Type")

            if not content_type:
                self.send_html(index_html_builder("ファイルが送信されていません。"), status=400)
                return

            temp_dir = Path(tempfile.mkdtemp(prefix="ocaml_upload_"))

            content_length = int(self.headers.get("Content-Length", "0"))

            if content_length <= 0:
                self.send_html(index_html_builder("ファイルが送信されていません。"), status=400)
                return

            body = self.rfile.read(content_length)

            raw_message = (
                b"Content-Type: " + content_type.encode("utf-8") +
                b"\r\nMIME-Version: 1.0\r\n\r\n" +
                body
            )

            message = BytesParser(policy=policy.default).parsebytes(raw_message)

            if not message.is_multipart():
                self.send_html(index_html_builder(".ml ファイルを選択してください。"), status=400)
                return

            upload_mode = "bulk"
            bulk_file_parts = []
            student_ids = []
            student_file_parts = []

            for part in message.iter_parts():
                disposition = part.get_content_disposition()

                if disposition != "form-data":
                    continue

                field_name = part.get_param("name", header="content-disposition")

                if field_name == "upload_mode":
                    upload_mode = get_form_text(part).strip() or "bulk"

                elif field_name == "files":
                    bulk_file_parts.append(part)

                elif field_name == "student_ids":
                    student_ids.append(get_form_text(part).strip())

                elif field_name == "student_files":
                    student_file_parts.append(part)

            saved_count = 0
            file_metadata = {}

            if upload_mode == "student":
                for index, part in enumerate(student_file_parts):
                    student_id = student_ids[index].strip() if index < len(student_ids) else ""
                    filename = Path(part.get_filename() or "").name

                    if not student_id:
                        continue

                    if not filename:
                        continue

                    if not filename.endswith(".ml"):
                        continue

                    payload = part.get_payload(decode=True)

                    if payload is None:
                        continue

                    safe_student_id = "".join(
                        ch for ch in student_id
                        if ch.isalnum() or ch in ("-", "_")
                    )

                    if not safe_student_id:
                        safe_student_id = "student"

                    save_name = "{}_{}_{}".format(
                        index + 1,
                        safe_student_id,
                        filename
                    )
                    save_path = temp_dir / save_name

                    with save_path.open("wb") as f:
                        f.write(payload)

                    file_metadata[save_name] = {
                        "student_id": student_id,
                        "original_filename": filename,
                        "order": index,
                    }

                    saved_count += 1

                if saved_count == 0:
                    self.send_html(
                        index_html_builder("学籍番号と .ml ファイルの組み合わせを入力してください。"),
                        status=400
                    )
                    return

            else:
                for index, part in enumerate(bulk_file_parts):
                    filename = Path(part.get_filename() or "").name

                    if not filename:
                        continue

                    if not filename.endswith(".ml"):
                        continue

                    payload = part.get_payload(decode=True)

                    if payload is None:
                        continue

                    save_name = "{}_{}".format(index + 1, filename)
                    save_path = temp_dir / save_name

                    with save_path.open("wb") as f:
                        f.write(payload)

                    file_metadata[save_name] = {
                        "student_id": "",
                        "original_filename": filename,
                        "order": index,
                    }

                    saved_count += 1

                if saved_count == 0:
                    self.send_html(index_html_builder(".ml ファイルがアップロードされていません。"), status=400)
                    return

            all_results, file_summaries = check_uploaded_files(temp_dir, file_metadata, checker_module=checker_module)

            html = result_html_builder(all_results, file_summaries)

            if self.path == "/check":
                html = add_first_period_score_badges(html, file_summaries)
                html = add_first_period_score_style(html)

            self.send_html(html)

        except Exception:
            err = traceback.format_exc()
            html = index_html_builder("実行中にエラーが発生しました。")
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
