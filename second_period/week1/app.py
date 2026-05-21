# -*- coding: utf-8 -*-

"""Second-period Week1 app scaffold.

This module provides dedicated UI entrypoints for 2期第1週 while reusing the
current 1期 page as an initial clone.
"""


def add_week1_title_style(html):
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
  font-size: 0.52em;
  font-weight: 950;
  line-height: 1;
  margin-bottom: 0.10em;
  letter-spacing: -0.06em;
  transform: translateX(-0.04em);
}
"""

    return html.replace("</style>", extra_css + "\n</style>")


def build_index_html(message=""):
    import web_app

    html = web_app.build_index_html(message)
    html = html.replace("action='/check'", "action='/period/2/week1/check'")
    html = html.replace("Ocaml 1期", "Ocaml 2期")
    html = html.replace("OCaml 1期", "OCaml 2期")
    html = html.replace("1期", "2期")

    html = html.replace(
        "OCaml<br>2期",
        'OCaml<br><span class="period-with-week"><span class="period-main">2期</span><span class="period-week">第1週</span></span>'
    )

    html = add_week1_title_style(html)

    return html


def build_result_html(all_results, file_summaries):
    import web_app

    html = web_app.build_result_html(all_results, file_summaries)
    html = html.replace("採点結果 - Ocaml 1期", "採点結果 - Ocaml 2期 第1週")
    html = html.replace("Ocaml 1期", "Ocaml 2期 第1週")
    html = html.replace("OCaml 1期", "OCaml 2期 第1週")
    html = html.replace("1期", "2期 第1週")

    return html