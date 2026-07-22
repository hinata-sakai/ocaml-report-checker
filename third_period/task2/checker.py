# -*- coding: utf-8 -*-

"""Automatic checker for third-period task 2 (the ``Vector`` module)."""

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
pass "vempty" (empty = []);;
''',
    ),
    make_test(
        "at",
        PRELUDE + r'''
let values = vector 3 [10; 20; 30; 40];;
pass "at first" (at 0 values = 10);;
pass "at last" (at 2 values = 30);;
let raises_empty index =
  try let _ = at index values in false with Vector.Empty -> true
;;
pass "at upper bound" (raises_empty 3);;
pass "at negative index" (raises_empty (-1));;
''',
    ),
    make_test(
        "vector",
        PRELUDE + r'''
pass "vector truncates" (vector 3 [1; 2; 3; 4] = [1; 2; 3]);;
pass "vector empty" (vector 0 [1; 2] = []);;
''',
    ),
    make_test(
        "vlength",
        PRELUDE + r'''
pass "vlength empty" (vlength (vempty ()) = 0);;
pass "vlength values" (vlength (vector 3 [1; 2; 3; 4]) = 3);;
''',
    ),
    make_test(
        "vshow",
        PRELUDE + r'''
vshow (vector 3 [1; 2; 3; 4]);;
print_newline ();;
print_endline "OK vshow";;
''',
        expected_output="1, 2, 3",
    ),
    make_test(
        "isempty",
        PRELUDE + r'''
pass "isempty empty" (isempty (vempty ()));;
pass "isempty values" (not (isempty (vector 1 [7; 8])));;
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
        + "\n\n(* ---- third period task2 checker test ---- *)\n"
        + test_code
        + "\n"
    )


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
            mode="w", suffix=".ml", encoding="utf-8", delete=False
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
        result.update(stdout=stdout, stderr=stderr)

        if completed.returncode != 0:
            return result
        if "NG " in stdout:
            result["status"] = "NG"
            return result
        if test.get("expected_output") not in (None, ""):
            if test["expected_output"] not in stdout:
                result["status"] = "NG"
                return result
        if not any(line.startswith("OK ") for line in stdout.splitlines()):
            result["status"] = "NG"
            return result

        result["status"] = "WARNING" if stderr.strip() else "OK"
        return result
    except subprocess.TimeoutExpired:
        result["stderr"] = "Timeout: 再帰が止まらない、または実行に時間がかかりすぎています。"
        return result
    except Exception as exc:
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
        summaries.append({"question": question, "status": status, "results": results})
    return summaries


def run_checker(ml_file):
    """Run all six automatic tests for third-period task 2."""
    return [run_one_test(ml_file, test) for test in TESTS]
