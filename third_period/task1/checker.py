# -*- coding: utf-8 -*-

"""Automatic checker for third-period task 1 (custom polymorphic lists)."""

import re
import subprocess
import tempfile
from pathlib import Path


OCAML_COMMAND = "ocaml"
TIMEOUT_SECONDS = 8

REQUIRED_FUNCTIONS = {
    "create",
    "unshift",
    "shift",
    "push",
    "pop",
    "size",
    "max",
    "min",
    "get",
    "indexOf",
    "set",
    "remove",
    "concat",
}

QUESTION_ORDER = [
    "create",
    "unshift",
    "shift",
    "push",
    "pop",
    "size",
    "max",
    "min",
    "get",
    "indexOf",
    "set",
    "remove",
    "concat",
    "extra",
]


def make_test(question, code):
    return {
        "question": str(question),
        "name": str(question),
        "code": code,
    }


PRELUDE = r'''
open List;;

let pass label condition =
  if condition then
    print_endline ("OK " ^ label)
  else
    print_endline ("NG " ^ label)
;;

let expect_int label actual expected =
  pass label (actual = expected)
;;

let expect_list label xs expected =
  let rec check i expected_values =
    match expected_values with
    | [] ->
        size xs = i
    | value :: rest ->
        size xs > i && get i xs = value && check (i + 1) rest
  in
  pass label (check 0 expected)
;;

let sample_l1 () =
  push 8 (unshift 10 (push 5 (unshift 2 (create ()))))
;;

let sample_l2 () =
  push 1 (unshift 12 (unshift 2 (create ())))
;;

let sample_l () =
  concat (sample_l1 ()) (sample_l2 ())
;;
'''


TESTS = [
    make_test(
        "create",
        PRELUDE + r'''
let l = create ();;
expect_int "create size" (size l) 0;;
''',
    ),

    make_test(
        "unshift",
        PRELUDE + r'''
let l = unshift 10 (create ());;
expect_int "unshift size" (size l) 1;;
expect_int "unshift first" (get 0 l) 10;;
''',
    ),

    make_test(
        "shift",
        PRELUDE + r'''
let l = sample_l ();;
let shifted = shift l;;
expect_list "shift" shifted [2; 5; 8; 12; 2; 1];;
''',
    ),

    make_test(
        "push",
        PRELUDE + r'''
let l = push 8 (create ());;
expect_int "push size" (size l) 1;;
expect_int "push first" (get 0 l) 8;;

let l2 = push 8 (unshift 10 (create ()));;
expect_list "push after unshift" l2 [10; 8];;
''',
    ),

    make_test(
        "pop",
        PRELUDE + r'''
let l = sample_l ();;
let popped = pop l;;
expect_list "pop" popped [10; 2; 5; 8; 12; 2];;
''',
    ),

    make_test(
        "size",
        PRELUDE + r'''
let l1 = sample_l1 ();;
let l2 = sample_l2 ();;
let l = sample_l ();;
expect_int "size empty" (size (create ())) 0;;
expect_int "size l1" (size l1) 4;;
expect_int "size l2" (size l2) 3;;
expect_int "size l" (size l) 7;;
''',
    ),

    make_test(
        "max",
        PRELUDE + r'''
let l1 = sample_l1 ();;
let l2 = sample_l2 ();;
let l = sample_l ();;
expect_int "max l1" (max l1) 10;;
expect_int "max l2" (max l2) 12;;
expect_int "max l" (max l) 12;;
''',
    ),

    make_test(
        "min",
        PRELUDE + r'''
let l1 = sample_l1 ();;
let l2 = sample_l2 ();;
let l = sample_l ();;
expect_int "min l1" (min l1) 2;;
expect_int "min l2" (min l2) 1;;
expect_int "min l" (min l) 1;;
''',
    ),

    make_test(
        "get",
        PRELUDE + r'''
let l = sample_l ();;
expect_int "get 0" (get 0 l) 10;;
expect_int "get 1" (get 1 l) 2;;
expect_int "get 2" (get 2 l) 5;;
expect_int "get 3" (get 3 l) 8;;
expect_int "get 4" (get 4 l) 12;;
expect_int "get 5" (get 5 l) 2;;
expect_int "get 6" (get 6 l) 1;;
''',
    ),

    make_test(
        "indexOf",
        PRELUDE + r'''
let l = sample_l ();;
expect_int "indexOf existing" (indexOf 12 l) 4;;
expect_int "indexOf missing" (indexOf 99 l) (-1);;
expect_int "indexOf first duplicated value" (indexOf 2 l) 1;;
''',
    ),

    make_test(
        "set",
        PRELUDE + r'''
let l = sample_l ();;
let set_one = set 1 0 l;;
let set_all = set 2 99 l;;
expect_list "set one" set_one [10; 2; 5; 8; 12; 2; 0];;
expect_list "set all" set_all [10; 99; 5; 8; 12; 99; 1];;
''',
    ),

    make_test(
        "remove",
        PRELUDE + r'''
let l = sample_l ();;
let remove_one = remove 5 l;;
let remove_all = remove 2 l;;
expect_list "remove one" remove_one [10; 2; 8; 12; 2; 1];;
expect_list "remove all" remove_all [10; 5; 8; 12; 1];;
''',
    ),

    make_test(
        "concat",
        PRELUDE + r'''
let l1 = sample_l1 ();;
let l2 = sample_l2 ();;
let l = concat l1 l2;;
expect_list "concat" l [10; 2; 5; 8; 12; 2; 1];;
''',
    ),

    {
        "question": "extra",
        "name": "extra",
        "extra": True,
        "code": "",
    },
]


def read_file_text(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return Path(path).read_text(encoding="utf-8", errors="replace")


def build_ocaml_script(student_code, test_code):
    return (
        student_code
        + "\n\n"
        + "(* ---- third period task1 checker test ---- *)\n"
        + test_code
        + "\n"
    )


def remove_ocaml_comments(code):
    """Remove simple OCaml comments for function detection."""
    return re.sub(r"\(\*.*?\*\)", "", code, flags=re.DOTALL)


def extract_list_module_body(code):
    """Extract body of module List = struct ... end when possible."""
    match = re.search(
        r"\bmodule\s+List\b(?:\s*:\s*sig.*?end)?\s*=\s*struct\b(.*?)\bend\b",
        code,
        flags=re.DOTALL,
    )

    if match:
        return match.group(1)

    match = re.search(
        r"\bmodule\s+List\s*=\s*struct\b(.*?)\bend\b",
        code,
        flags=re.DOTALL,
    )

    if match:
        return match.group(1)

    return code


def count_extra_functions(code):
    """Count additional functions defined directly under module List, up to two.

    Local helper functions and local variables such as
    `let rec aux ...`, `let m = ... in`, and `let res = ... in`
    are not counted.
    """

    code = remove_ocaml_comments(code)
    body = extract_list_module_body(code)

    lines = body.splitlines()
    extra_names = set()

    for i, line in enumerate(lines):
        match = re.match(
            r"^[ \t]*let\s+(?:rec\s+)?(?P<name>[a-zA-Z_][a-zA-Z0-9_']*)\b(?P<rest>.*)$",
            line,
        )

        if not match:
            continue

        name = match.group("name")
        rest = match.group("rest").strip()

        if name in REQUIRED_FUNCTIONS:
            continue

        if name.startswith("_"):
            continue

        if name in {
            "l",
            "l1",
            "l2",
            "x",
            "y",
            "m",
            "res",
            "result",
            "answer",
            "test",
            "sample",
            "sample_l",
            "sample_l1",
            "sample_l2",
        }:
            continue

        previous = ""

        for j in range(i - 1, -1, -1):
            candidate = lines[j].strip()

            if candidate:
                previous = candidate
                break

        if previous.endswith("->"):
            continue

        if previous.endswith("="):
            continue

        if previous in {"else", "then", "in"}:
            continue

        if previous.endswith("else"):
            continue

        if previous.endswith("then"):
            continue

        if previous.endswith("in"):
            continue

        if re.search(r"\bin\s*$", previous):
            continue

        is_function_like = False

        if rest.startswith("="):
            if rest.startswith("= function"):
                is_function_like = True
            else:
                is_function_like = False
        else:
            is_function_like = True

        if not is_function_like:
            continue

        extra_names.add(name)

    return min(2, len(extra_names))


def run_one_test(ml_file, test):
    result = {
        "question": str(test["question"]),
        "test": test["name"],
        "status": "ERROR",
        "stdout": "",
        "stderr": "",
    }

    student_code = read_file_text(ml_file)

    if test.get("extra"):
        count = count_extra_functions(student_code)
        extra_points = count * 2

        if extra_points > 0:
            stdout = "OK extra: 追加の関数があります。確認してください。\n"
        else:
            stdout = "OK extra: 追加の関数はありません。\n"

        result.update(
            status="OK",
            stdout=stdout,
            extra_points=extra_points,
            extra_count=count,
        )

        return result

    script = build_ocaml_script(student_code, test["code"])
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".ml",
            encoding="utf-8",
            delete=False,
        ) as file:
            file.write(script)
            temp_path = file.name

        completed = subprocess.run(
            [OCAML_COMMAND, temp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=TIMEOUT_SECONDS,
        )

        stdout = completed.stdout or ""
        stderr = completed.stderr or ""

        result["stdout"] = stdout
        result["stderr"] = stderr

        if completed.returncode != 0:
            result["status"] = "ERROR"
            return result

        if "NG " in stdout:
            result["status"] = "NG"
            return result

        ok_lines = [
            line for line in stdout.splitlines()
            if line.startswith("OK ")
        ]

        if not ok_lines:
            result["status"] = "NG"
            return result

        if stderr.strip():
            result["status"] = "WARNING"
        else:
            result["status"] = "OK"

        return result

    except subprocess.TimeoutExpired:
        result["status"] = "ERROR"
        result["stderr"] = "Timeout: 再帰が止まらない、または実行に時間がかかりすぎています。"
        return result

    except Exception as exc:
        result["status"] = "ERROR"
        result["stderr"] = repr(exc)
        return result

    finally:
        if temp_path:
            try:
                Path(temp_path).unlink()
            except Exception:
                pass


def question_sort_key(question):
    question = str(question)

    if question in QUESTION_ORDER:
        return [QUESTION_ORDER.index(question)]

    return [len(QUESTION_ORDER), question]


def summarize_by_question(file_results):
    grouped = {}

    for result in file_results:
        question = str(result.get("question", ""))
        grouped.setdefault(question, []).append(result)

    summaries = []

    for question in sorted(grouped.keys(), key=question_sort_key):
        question_results = grouped[question]
        statuses = [r.get("status") for r in question_results]

        if "ERROR" in statuses:
            status = "ERROR"
        elif "NG" in statuses:
            status = "NG"
        elif "WARNING" in statuses:
            status = "WARNING"
        else:
            status = "OK"

        summary = {
            "question": question,
            "status": status,
            "results": question_results,
        }

        if question == "extra":
            summary["extra_points"] = max(
                r.get("extra_points", 0) for r in question_results
            )

        summaries.append(summary)

    return summaries


def run_checker(ml_file):
    """Run all automatic tests for third-period task 1."""
    return [run_one_test(ml_file, test) for test in TESTS]