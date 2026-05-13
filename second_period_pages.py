# -*- coding: utf-8 -*-

"""Pages for the second OCaml period.

The main web_app.py file owns the shared carousel renderer. 2期-specific
selection data lives here so future 2期 pages can grow without making
web_app.py larger.
"""


def build_week_select_html(build_carousel_select_html):
    """Build the 2期 week selection page using the shared carousel layout."""
    items = [
        {"label": "第１週", "href": "#", "coming_soon": True},
        {"label": "第２週", "href": "#", "coming_soon": True},
        {"label": "第３週", "href": "#", "coming_soon": True},
    ]
    return build_carousel_select_html("2期 週選択", items, initial_index=0, back_href="/period")