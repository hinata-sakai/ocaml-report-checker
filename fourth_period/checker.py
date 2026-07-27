"""Static, style-tolerant checker for the SProlog lexer/parser assignment."""

import re
from pathlib import Path

QUESTION_POINTS = {
    "1-1-cid-reserved": 5,
    "1-2-vid": 5,
    "1-3-num": 5,
    "1-4-to": 5,

    "2-1-terms-right-recursion": 5,
    "2-2-args-right-recursion": 5,

    **{
        "3-{}-{}".format(i, name): 2
        for i, name in enumerate(
            (
                "clause",
                "to-opt",
                "command",
                "term",
                "terms",
                "predicate",
                "args",
                "expr",
                "tail-opt",
                "list",
                "id",
            ),
            1,
        )
    },

    "5-multiple-goals": 10,

    "6-1-line-count": 5,
    "6-2-error-handle": 5,

    "7-1-arithmexp": 5,
    "7-2-expr-uses-arithmexp": 5,

    "8-is-arithmexp": 10,
}

TOTAL_POINTS = 92
QUESTION_ORDER = list(QUESTION_POINTS)


def _clean(source):
    """Remove OCaml comments for simpler static checks."""
    return re.sub(r"\(\*.*?\*\)", " ", source, flags=re.S)


def _function(source, name):
    """Extract a rough function body for `let rec name` or `and name`."""
    match = re.search(
        r"\b(?:let\s+rec|and)\s+"
        + re.escape(name)
        + r"\b.*?=(.*?)(?=\n\s*(?:and|let)\s+[a-zA-Z_]|\Z)",
        source,
        re.S,
    )
    return match.group(1) if match else ""


def _has(text, *patterns):
    """Return True when all regex patterns are found."""
    return all(re.search(pattern, text, re.I | re.S) for pattern in patterns)


def _result(question, passed, detail):
    return {
        "question": question,
        "test": detail,
        "status": "OK" if passed else "NG",
        "stdout": "",
        "stderr": "" if passed else detail,
    }


def _contains_comma_token(text):
    """Detect L.ONE ',' / ONE ',' / ONE \",\" style comma token checks."""
    return bool(
        re.search(r"ONE\s*['\"]\s*,\s*['\"]", text, re.S)
        or re.search(r"L\.ONE\s*['\"]\s*,\s*['\"]", text, re.S)
    )


def _is_not_direct_left_recursive(body, name):
    """
    Return True when the function body does not immediately call itself.

    Left-recursive parser implementations often begin with terms() or args().
    Right-recursive versions should first consume term()/expr()/arithmexp().
    """
    return not re.match(r"\s*" + re.escape(name) + r"\s*\(", body)


def _terms_is_right_recursive(terms_body, source):
    """
    Accept both styles:

    1. Split helper style:
       terms() = term(); terms_opt()
       terms_opt() = "," term terms_opt | ε

    2. Direct right-recursive style:
       terms() =
         term();
         match !tok with
         | L.ONE ',' -> eat ...; terms()
         | _ -> ()
    """
    if not terms_body:
        return False

    has_term_first = re.search(r"term\s*\(\s*\)", terms_body) is not None
    if not has_term_first:
        return False

    if not _is_not_direct_left_recursive(terms_body, "terms"):
        return False

    has_comma = _contains_comma_token(terms_body) or _contains_comma_token(source)

    has_helper_style = re.search(
        r"terms(?:_opt|_tail|'|opt|tail)\s*\(",
        source,
        re.S,
    ) is not None

    has_direct_right_recursion = re.search(
        r"ONE\s*['\"]\s*,\s*['\"].*?terms\s*\(\s*\)",
        terms_body,
        re.S,
    ) is not None

    return bool(has_comma and (has_helper_style or has_direct_right_recursion))


def _args_is_right_recursive(args_body, source):
    """
    Accept both styles:

    1. Split helper style:
       args() = expr(); args_opt()
       args_opt() = "," expr args_opt | ε

    2. Direct right-recursive style:
       args() =
         expr();
         match !tok with
         | L.ONE ',' -> eat ...; args()
         | _ -> ()

    Also accept arithmexp() instead of expr() after arithmetic extension.
    """
    if not args_body:
        return False

    has_expr_first = re.search(r"(?:expr|arithmexp)\s*\(\s*\)", args_body) is not None
    if not has_expr_first:
        return False

    if not _is_not_direct_left_recursive(args_body, "args"):
        return False

    has_comma = _contains_comma_token(args_body) or _contains_comma_token(source)

    has_helper_style = re.search(
        r"args(?:_opt|_tail|'|opt|tail)\s*\(",
        source,
        re.S,
    ) is not None

    has_direct_right_recursion = re.search(
        r"ONE\s*['\"]\s*,\s*['\"].*?args\s*\(\s*\)",
        args_body,
        re.S,
    ) is not None

    return bool(has_comma and (has_helper_style or has_direct_right_recursion))


def _expr_is_valid(expr_body):
    """
    Accept either the original expr implementation or the arithmetic-extension style.

    Original style:
      expr handles CID / VID / NUM / list / tail_opt directly.

    Extended style:
      expr() = arithmexp()
    """
    if not expr_body:
        return False

    calls_arithmexp = re.search(r"arithmexp\s*\(\s*\)", expr_body) is not None

    original_expr_style = _has(
        expr_body,
        r"\bCID\b",
        r"\bVID\b",
        r"\bNUM\b",
        r"tail_opt",
        r"list\s*\(",
    )

    return bool(calls_arithmexp or original_expr_style)


def run_checker(ml_file):
    try:
        source = _clean(Path(ml_file).read_text(encoding="utf-8", errors="replace"))
    except OSError as exc:
        return [
            {
                "question": q,
                "test": "read",
                "status": "ERROR",
                "stdout": "",
                "stderr": str(exc),
            }
            for q in QUESTION_ORDER
        ]

    f = lambda name: _function(source, name)  # noqa: E731

    terms = f("terms")
    args = f("args")
    command = f("command")
    expr = f("expr")
    term = f("term")

    checks = {
        "1-1-cid-reserved": _has(
            source,
            r"\bCID\b",
            r"\bOPEN\b",
            r"\bQUIT\b",
            r"\bIS\b",
            r"identifier",
            r"['\"]open['\"]",
            r"['\"]quit['\"]",
            r"['\"]is['\"]",
            r"['\"]a['\"]\s*<=?|>=?\s*['\"]a['\"]",
        ),

        "1-2-vid": _has(
            source,
            r"\bVID\b",
            r"['\"]A['\"]\s*<=?|>=?\s*['\"]A['\"]",
        ),

        "1-3-num": _has(
            source,
            r"\bNUM\b",
            r"integer",
            r"['\"]0['\"]\s*<=?|>=?\s*['\"]0['\"]",
        ),

        "1-4-to": _has(
            source,
            r"\bTO\b",
            r"['\"]:['\"]",
            r"['\"]-['\"]",
            r"read\s*\(\s*\)",
            r"lookahead\s*\(\s*\)",
        ),

        # 問2：右再帰
        "2-1-terms-right-recursion": _terms_is_right_recursive(terms, source),
        "2-2-args-right-recursion": _args_is_right_recursive(args, source),

        # 問3：構文解析器
        "3-1-clause": _has(
            f("clause"),
            r"(?:term|predicate)\s*\(",
            r"to_opt|TO",
            r"['\"]\.['\"]",
        ),

        "3-2-to-opt": _has(
            f("to_opt"),
            r"\bTO\b",
            r"terms\s*\(",
        ),

        "3-3-command": _has(
            command,
            r"\bQUIT\b",
            r"\bOPEN\b",
            r"\bCID\b",
            r"(?:term|terms)\s*\(",
            r"['\"]\.['\"]",
        ),

        "3-4-term": _has(
            term,
            r"predicate\s*\(",
            r"['\"]\(['\"]",
            r"['\"]\)['\"]",
        ),

        "3-5-terms": bool(
            terms
            and re.search(r"term\s*\(", terms)
            and _contains_comma_token(source)
        ),

        "3-6-predicate": _has(
            f("predicate"),
            r"\bCID\b",
            r"args\s*\(",
            r"['\"]\(['\"]",
            r"['\"]\)['\"]",
        ),

        "3-7-args": bool(
            args
            and re.search(r"(?:expr|arithmexp)\s*\(", args)
            and _contains_comma_token(source)
        ),

        # expr() = arithmexp() の形も正解にする
        "3-8-expr": _expr_is_valid(expr),

        "3-9-tail-opt": _has(
            f("tail_opt"),
            r"args\s*\(",
            r"['\"]\(['\"]",
            r"['\"]\)['\"]",
        ),

        "3-10-list": _has(
            f("list"),
            r"(?:expr|arithmexp)\s*\(",
            r"list_opt",
        ),

        "3-11-id": _has(
            f("id"),
            r"\bCID\b",
            r"\bVID\b",
            r"\bNUM\b",
        ),

        # 問5：複数述語
        "5-multiple-goals": bool(
            command
            and re.search(r"terms\s*\(", command)
        ),

        # 問6：行番号付きエラー処理
        "6-1-line-count": _has(
            source,
            r"\b(?:line|line_no|lineno|row|count_line)\w*\b",
            r"['\"]\\n['\"]",
            r"(?:incr\s+\w+|:=\s*!?\w+\s*\+\s*1)",
        ),

        "6-2-error-handle": _has(
            source,
            r"\btry\b",
            r"\bwith\b",
            r"Syntax_error",
            r"(?:print_string|print_endline|Printf\.printf)",
        ),

        # 問7：算術式
        "7-1-arithmexp": _has(
            source,
            r"\barithmexp\b",
            r"\barithmterm\b",
            r"\barithmfactor\b",
            r"['\"]\+['\"]",
            r"['\"]-['\"]",
            r"['\"]\*['\"]",
            r"['\"]/['\"]",
        ),

        "7-2-expr-uses-arithmexp": bool(
            re.search(r"arithmexp\s*\(", expr + args + term)
        ),

        # 問8：VID IS arithmexp
        "8-is-arithmexp": bool(
            re.search(r"\bVID\b.*?\bIS\b.*?arithmexp\s*\(", term, re.S)
        ),
    }

    return [_result(q, checks[q], q) for q in QUESTION_ORDER]


def summarize_by_question(results):
    return [
        {
            "question": q,
            "status": next(r["status"] for r in results if r["question"] == q),
            "results": [r for r in results if r["question"] == q],
        }
        for q in QUESTION_ORDER
    ]