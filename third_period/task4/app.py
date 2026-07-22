# -*- coding: utf-8 -*-

"""Upload and result pages for third-period task 4."""


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
"""
    return html.replace("</style>", extra_css + "\n</style>", 1)


def build_index_html(message=""):
    import web_app

    html = web_app.build_index_html(message)
    html = html.replace("href='/period'>選択画面へ戻る</a>", "href='/period/3'>選択画面へ戻る</a>")
    html = html.replace("action='/check'", "action='/period/3/task4/check'")
    html = html.replace("Ocaml 1期", "OCaml 3期 課題4")
    html = html.replace("OCaml 1期", "OCaml 3期 課題4")
    html = html.replace(
        "OCaml<br>1期",
        'OCaml<br><span class="period-with-week"><span class="period-main">3期</span><span class="period-week">課題4</span></span>'
    )
    html = add_task_title_style(html)
    return html


def build_result_html(all_results, file_summaries):
    import web_app

    html = web_app.build_result_html(all_results, file_summaries)
    html = html.replace("Ocaml 1期", "OCaml 3期 課題4")
    html = html.replace("OCaml 1期", "OCaml 3期 課題4")
    return html
