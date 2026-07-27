"""Selection page for the fourth OCaml period."""


def build_task_select_html(build_carousel_select_html):
    return build_carousel_select_html(
        "4期 課題選択",
        [{"label": "課題1\nSProlog", "href": "/period/4/task1"}],
        initial_index=0,
        back_href="/period",
    )
