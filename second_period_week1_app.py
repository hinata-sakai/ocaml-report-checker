# -*- coding: utf-8 -*-

"""Second-period Week1 app scaffold.

This module provides dedicated UI entrypoints for 2期第1週 while reusing the
current 1期 page as an initial clone.
"""


def build_index_html(message=""):
    import web_app

    html = web_app.build_index_html(message)
    return html.replace("action='/check'", "action='/period/2/week1/check'")


def build_result_html(all_results, file_summaries):
    import web_app

    html = web_app.build_result_html(all_results, file_summaries)
    return html.replace("採点結果 - Ocaml 1期", "採点結果 - Ocaml 2期 第1週")
