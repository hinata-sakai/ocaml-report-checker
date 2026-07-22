# -*- coding: utf-8 -*-

"""Upload and result pages for third-period task 2."""


def build_index_html(message=""):
    import web_app

    html = web_app.build_index_html(message)
    html = html.replace("href='/period'>選択画面へ戻る</a>", "href='/period/3'>選択画面へ戻る</a>")
    html = html.replace("action='/check'", "action='/period/3/task2/check'")
    html = html.replace("Ocaml 1期", "OCaml 3期 課題2")
    html = html.replace("OCaml 1期", "OCaml 3期 課題2")
    html = html.replace("OCaml<br>1期", "OCaml<br>3期 課題2")
    return html


def build_result_html(all_results, file_summaries):
    import web_app

    html = web_app.build_result_html(all_results, file_summaries)
    html = html.replace("Ocaml 1期", "OCaml 3期 課題2")
    html = html.replace("OCaml 1期", "OCaml 3期 課題2")
    return html
