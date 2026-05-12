# -*- coding: utf-8 -*-

from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import tempfile
import shutil
from email.parser import BytesParser
from email import policy
import traceback

import run_checker


import os

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
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
    total_files = len(file_summaries)
    total_questions = sum(summary.get("total", 0) for summary in file_summaries)
    total_ok = sum(summary.get("ok", 0) for summary in file_summaries)
    overall_rate = round((total_ok / total_questions) * 100) if total_questions else 0

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
      var(--poster-paper) 0%,
      #f7f7f3 44%,
      var(--poster-mint) 44%,
      var(--poster-mint) 100%
    );
  color: var(--poster-ink);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.result-page {
  position: relative;
  min-height: 100vh;
  padding: 48px 28px 64px;
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

.result-overview {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}

.overview-card {
  padding: 18px 20px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.78);
  box-shadow: 0 16px 38px rgba(24, 88, 59, 0.14);
}

.overview-label {
  margin: 0 0 8px;
  color: rgba(11, 11, 13, 0.56);
  font-size: 12px;
  font-weight: 950;
  letter-spacing: 0.06em;
}

.overview-value {
  margin: 0;
  font-size: 30px;
  font-weight: 950;
  letter-spacing: -0.04em;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 22px;
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
  background: linear-gradient(90deg, var(--poster-alert), #ff9a54);
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
  font-size: clamp(40px, 6vw, 72px);
  line-height: 0.95;
  font-weight: 950;
  letter-spacing: -0.08em;
}

.score-sub {
  color: rgba(11, 11, 13, 0.58);
  font-size: 16px;
  font-weight: 900;
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

.wrong-block {
  padding: 16px 18px;
  border-radius: 22px;
  background: rgba(134, 221, 177, 0.22);
  border: 1px solid rgba(37, 138, 89, 0.18);
}

.needs-review .wrong-block {
  background: var(--poster-alert-soft);
  border-color: rgba(255, 107, 72, 0.25);
}

.wrong-title {
  margin: 0 0 10px;
  color: rgba(11, 11, 13, 0.64);
  font-size: 13px;
  font-weight: 950;
  letter-spacing: 0.04em;
}

.wrong-none {
  margin: 0;
  color: var(--poster-mint-dark);
  font-size: 15px;
  font-weight: 900;
}

.wrong-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.wrong-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 46px;
  padding: 8px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  color: #b83217;
  font-size: 14px;
  font-weight: 950;
  box-shadow: 0 8px 18px rgba(181, 55, 24, 0.12);
}

.actions {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.back-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 52px;
  padding: 0 28px;
  border-radius: 999px;
  background: var(--poster-ink);
  color: white;
  text-decoration: none;
  font-size: 16px;
  font-weight: 950;
  box-shadow: 0 14px 28px rgba(11, 11, 13, 0.24);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.back-link:hover {
  transform: translateY(-2px);
  background: #1f1f22;
  box-shadow: 0 18px 32px rgba(11, 11, 13, 0.30);
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

  .result-hero,
  .result-overview {
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
}
</style>
""")
    html.append("</head>")
    html.append("<body>")
    html.append("<main class='result-page'>")
    html.append("<div class='result-shell'>")
    html.append("<section class='result-hero'>")
    html.append("<div>")
    html.append("<div class='badge'>Report Checker</div>")
    html.append("<h1 class='result-title'>採点<br>結果</h1>")
    html.append("</div>")
    html.append("<div class='hero-copy'>")
    html.append("<p class='kicker'>Ocaml 1期 / Result</p>")
    html.append("<p class='lead'>ファイルごとの正解数と、確認が必要な問をまとめて表示しています。</p>")
    html.append("</div>")
    html.append("</section>")

    html.append("<section class='result-grid' aria-label='ファイルごとの採点結果'>")
    for summary in file_summaries:
        filename = html_escape(summary["file"])
        ok = summary["ok"]
        total = summary["total"]
        wrong_questions = [
            q_summary["question"]
            for q_summary in summary.get("questions", [])
            if q_summary.get("status") != "OK"
        ]
        score_rate = round((ok / total) * 100) if total else 0
        card_class = "result-card needs-review" if wrong_questions else "result-card"
        status_label = "確認が必要" if wrong_questions else "全問正解"

        html.append("<article class='{}'>".format(card_class))
        html.append("<div class='card-top'>")
        html.append("<h2 class='file-name'>{}</h2>".format(filename))
        html.append("<span class='status-pill'>{}</span>".format(status_label))
        html.append("</div>")
        html.append("<div class='score-line'>")
        html.append("<span class='score-main'>{}問中 {}問</span>".format(total, ok))
        html.append("<span class='score-sub'>正解</span>")
        html.append("</div>")
        html.append("<div class='progress' aria-label='正解率 {}%'>".format(score_rate))
        html.append("<span class='progress-bar' style='--score-width: {}%;'></span>".format(score_rate))
        html.append("</div>")
        html.append("<div class='wrong-block'>")
        html.append("<p class='wrong-title'>間違えた問</p>")
        if wrong_questions:
            html.append("<div class='wrong-tags'>")
            for question in wrong_questions:
                html.append("<span class='wrong-tag'>Q{}</span>".format(html_escape(question)))
            html.append("</div>")
        else:
            html.append("<p class='wrong-none'>なし</p>")
        html.append("</div>")
        html.append("</article>")
    html.append("</section>")

    html.append("<div class='actions'>")
    html.append("<a class='back-link' href='/upload'>別のファイルを採点する</a>")
    html.append("</div>")
    html.append("</div>")
    html.append("</main>")
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
    html.append("<a class='start-button' href='/term'>採点をはじめる</a>")
    html.append("</div>")
    html.append("</div>")
    html.append("</body>")
    html.append("</html>")

    return "\n".join(html)


def build_term_select_html():
    items = [
        {"label": "前期\nocaml演習", "href": "/period"},
        {"label": "後期\nJava演習", "href": "#", "coming_soon": True},
    ]
    return build_carousel_select_html("前期・後期選択", items, initial_index=0, back_href="/")


def build_period_select_html():
    items = [
        {"label": "1期\nocaml演習", "href": "/upload"},
        {"label": "2期\nocaml演習", "href": "#", "coming_soon": True},
        {"label": "3期\nocaml演習", "href": "#", "coming_soon": True},
        {"label": "4期\nocaml演習", "href": "#", "coming_soon": True},
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

.page {
  position: relative;
  z-index: 4;
  min-height: 100vh;
  text-align: center;
  padding-bottom: 28px;
  box-sizing: border-box;
}

.back-button {
  position: fixed;
  top: 40%;
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
  overflow: hidden;
  position: relative;
  padding: 24px 0 8px;
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
  margin-top: 36px;
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
    html.append("<title>Ocaml 1期</title>")
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
    linear-gradient(180deg, var(--poster-paper) 0%, var(--poster-paper) 44%, var(--poster-mint) 44%, var(--poster-mint) 100%);
}

.upload-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  padding: 42px 24px 56px;
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

.upload-page::after {
  content: "";
  position: absolute;
  top: 0;
  bottom: 42%;
  left: 31%;
  width: 3px;
  background: rgba(255, 255, 255, 0.85);
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

.arrow-mark {
  width: 74px;
  height: 74px;
  margin-top: 42px;
  border-top: 5px solid var(--poster-ink);
  border-right: 5px solid var(--poster-ink);
  transform: rotate(45deg);
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

  .arrow-mark {
    display: none;
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
    html.append("<section class='hero'>")
    html.append("<div class='hero-top'>")
    html.append("<div>")
    html.append("<div class='badge'>Report Checker</div>")
    html.append("<h1>Ocaml<br>1期</h1>")
    html.append("<div class='arrow-mark' aria-hidden='true'></div>")
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

    html.append("<form method='POST' enctype='multipart/form-data' action='/check'>")
    html.append("<p class='form-title'>ファイルの選択</p>")
    html.append("<label class='file-drop'>")
    html.append("<span class='file-drop-title'>.ml ファイルをアップロード</span>")
    html.append("<span class='file-drop-text'>複数選択できます。選択したファイル名は下に表示されます。</span>")
    html.append("<input id='file-input' type='file' name='files' accept='.ml' multiple required>")
    html.append("</label>")
    html.append("<div class='selected-files is-empty' id='selected-files' aria-live='polite'>")
    html.append("<p class='selected-files-title'>選択中のファイル</p>")
    html.append("<ul id='selected-file-list'><li>まだファイルが選択されていません。</li></ul>")
    html.append("</div>")
    html.append("<button class='submit-button' type='submit'>採点を実行</button>")
    html.append("</form>")

    html.append("<p class='note'>")
    html.append("注意: Exception が出る実行例を提出ファイル内で直接実行している場合、読み込み時点で ERROR になることがあります。")
    html.append("課題文の指示通り、例外が出る呼び出しはコメントアウトしてください。")
    html.append("</p>")
    html.append("</div>")
    html.append("</div>")
    html.append("</section>")
    html.append("</main>")
    html.append("""
<script>
document.addEventListener('DOMContentLoaded', function () {
  const fileInput = document.getElementById('file-input');
  const selectedFiles = document.getElementById('selected-files');
  const selectedFileList = document.getElementById('selected-file-list');

  function updateSelectedFiles() {
    const files = Array.from(fileInput.files || []);
    selectedFileList.innerHTML = '';

    if (files.length === 0) {
      selectedFiles.classList.add('is-empty');
      const emptyItem = document.createElement('li');
      emptyItem.textContent = 'まだファイルが選択されていません。';
      selectedFileList.appendChild(emptyItem);
      return;
    }

    selectedFiles.classList.remove('is-empty');
    files.forEach(function (file) {
      const item = document.createElement('li');
      item.textContent = file.name;
      selectedFileList.appendChild(item);
    });
  }

  fileInput.addEventListener('change', updateSelectedFiles);
});
</script>
""")
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
        elif self.path == "/term" or self.path.startswith("/term?"):
            self.send_html(build_term_select_html())
        elif self.path == "/period" or self.path.startswith("/period?"):
            self.send_html(build_period_select_html())
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

            content_length = int(self.headers.get("Content-Length", "0"))

            if content_length <= 0:
                self.send_html(build_index_html("ファイルが送信されていません。"), status=400)
                return

            body = self.rfile.read(content_length)

            raw_message = (
                b"Content-Type: " + content_type.encode("utf-8") +
                b"\r\nMIME-Version: 1.0\r\n\r\n" +
                body
            )

            message = BytesParser(policy=policy.default).parsebytes(raw_message)

            if not message.is_multipart():
                self.send_html(build_index_html(".ml ファイルを選択してください。"), status=400)
                return

            saved_count = 0

            for part in message.iter_parts():
                disposition = part.get_content_disposition()

                if disposition != "form-data":
                    continue

                field_name = part.get_param("name", header="content-disposition")

                if field_name != "files":
                    continue

                filename = Path(part.get_filename() or "").name

                if not filename:
                    continue

                if not filename.endswith(".ml"):
                    continue

                payload = part.get_payload(decode=True)

                if payload is None:
                    continue

                save_path = temp_dir / filename

                with save_path.open("wb") as f:
                    f.write(payload)

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