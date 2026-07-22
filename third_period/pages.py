# -*- coding: utf-8 -*-

"""Selection pages for the third OCaml period."""


def build_task_select_html(build_carousel_select_html):
    """Build the 3期 assignment selection page with the shared carousel."""
    items = [
        {"label": "課題1", "href": "/period/3/task1"},
        {"label": "課題2", "href": "/period/3/task2"},
        {"label": "課題3", "href": "/period/3/task3"},
        {"label": "課題4", "href": "/period/3/task4"},
    ]
    return build_carousel_select_html(
        "3期 課題選択", items, initial_index=0, back_href="/period"
    )
