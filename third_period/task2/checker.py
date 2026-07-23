# -*- coding: utf-8 -*-

"""Automatic checker for third-period task 2 (the ``Vector`` module)."""

import re
import subprocess
import tempfile
from pathlib import Path


OCAML_COMMAND = "ocaml"
TIMEOUT_SECONDS = 8

QUESTION_ORDER = ["vempty", "at", "vector", "vlength", "vshow", "isempty"]


def make_test(question, code, expected_output=None):
    test = {"question": question, "name": question, "code": code}

    if expected_output is not None:
        test["expected_output"] = expected_output

    return test


PRELUDE = r'''
open Vector;;

let pass label condition =
  if condition then print_endline ("OK " ^ label)
  else print_endline ("NG " ^ label)
;;
'''


TESTS = [
    make_test(
        "vempty",
        PRELUDE + r'''
let empty = vempty ();;
pass "vempty empty list" (empty = []);;
pass "vempty is empty" (isempty empty);;
''',
    ),

    make_test(
        "vector",
        PRELUDE + r'''
let values = vector [1; 2; 3; 4];;
pass "vector creates values" (values = [1; 2; 3; 4]);;

let empty = vector [];;
pass "vector creates empty" (empty = []);;
''',
    ),

    make_test(
        "at",
        PRELUDE + r'''
let values = vector [10; 20; 30; 40];;

pass "at first" (at 0 values = 10);;
pass "at middle" (at 2 values = 30);;
pass "at last" (at 3 values = 40);;

let raises_empty index =
  try
    let _ = at index values in
    false
  with
  | Vector.Empty -> true
  | _ -> false
;;

pass "at upper bound" (raises_empty 4);;
''',
    ),

    make_test(
        "vlength",
        PRELUDE + r'''
pass "vlength empty" (vlength (vempty ()) = 0);;

let values = vector [1; 2; 3; 4];;
pass "vlength values" (vlength values = 4);;
''',
    ),

    make_test(
        "vshow",
        PRELUDE + r'''
let values = vector [1; 2; 3; 4];;
vshow values;;
print_newline ();;
print_endline "OK vshow";;
''',
        expected_output="1,2,3,4",
    ),

    make_test(
        "isempty",
        PRELUDE + r'''
pass "isempty empty" (isempty (vempty ()));;

let values = vector [7; 8];;
pass "isempty values" (not (isempty values));;
''',
    ),
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
        + "(* ---- third period task2 checker test ---- *)\n"
        + test_code
        + "\n"
    )


def normalize_output(text):
    """Normalize output for vshow.

    This allows both:
    1,2,3,4
    and:
    1, 2, 3, 4
    """

    return re.sub(r"\s+", "", text)


def run_one_test(ml_file, test):
    result = {
        "question": str(test["question"]),
        "test": test["name"],
        "status": "ERROR",
        "stdout": "",
        "stderr": "",
    }

    script = build_ocaml_script(read_file_text(ml_file), test["code"])
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

        expected_output = test.get("expected_output")

        if expected_output not in (None, ""):
            normalized_stdout = normalize_output(stdout)
            normalized_expected = normalize_output(expected_output)

            if normalized_expected not in normalized_stdout:
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
            except OSError:
                pass


def question_sort_key(question):
    question = str(question)

    if question in QUESTION_ORDER:
        return (QUESTION_ORDER.index(question), "")

    return (len(QUESTION_ORDER), question)


def summarize_by_question(file_results):
    grouped = {}

    for result in file_results:
        question = str(result.get("question", ""))
        grouped.setdefault(question, []).append(result)

    summaries = []

    for question in sorted(grouped, key=question_sort_key):
        results = grouped[question]
        statuses = [result.get("status") for result in results]

        if "ERROR" in statuses:
            status = "ERROR"
        elif "NG" in statuses:
            status = "NG"
        elif "WARNING" in statuses:
            status = "WARNING"
        else:
            status = "OK"

        summaries.append({
            "question": question,
            "status": status,
            "results": results,
        })

    return summaries


def run_checker(ml_file):
    """Run all six automatic tests for third-period task 2."""
    return [run_one_test(ml_file, test) for test in TESTS]