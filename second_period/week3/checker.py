# -*- coding: utf-8 -*-

"""Checker for OCaml second period, week 3.

Week 3 is the sorting-algorithm assignment.  Each auto-graded question lets
students choose at least one implementation from a set of candidate functions,
so this checker runs each candidate independently and then summarizes results by
question on the Python side.

Auto-graded questions:
- Q1   Simple sorting algorithm, one of exchange_sort/selection_sort/insertion_sort
- Q2   Divide-and-conquer sorting algorithm, one of merge_sort/quick_sort
- Q3-1 Simple sorting algorithm with comparison count, one of *_sort_c
- Q3-2 Divide-and-conquer sorting algorithm with comparison count, one of *_sort_c

Report/PDF-only questions 4-1, 4-2, 5-1, 5-2, and 5-3 are intentionally not
auto-graded.
"""

import subprocess
import tempfile
from pathlib import Path


OCAML_COMMAND = "ocaml"
TIMEOUT_SECONDS = 8


SORT_TEST_CODE_TEMPLATE = r'''
let show_int_list xs =
  "[" ^ String.concat "; " (List.map string_of_int xs) ^ "]"
;;

let test_cases = [
  [];
  [1];
  [3; 1; 2];
  [5; 4; 3; 2; 1];
  [1; 2; 3; 4; 5];
  [3; 1; 3; 2; 1];
  [-1; 3; 0; -5; 2];
];;

let assert_sorted label input actual =
  let expected = List.sort compare input in
  if actual = expected then
    print_endline ("OK " ^ label ^ " " ^ show_int_list input)
  else
    Printf.printf "NG %s %s: expected %s but got %s\n"
      label (show_int_list input) (show_int_list expected) (show_int_list actual)
;;

List.iter (fun input -> assert_sorted "{function_name}" input ({function_name} input)) test_cases;;
'''


COUNT_SORT_TEST_CODE_TEMPLATE = r'''
let show_int_list xs =
  "[" ^ String.concat "; " (List.map string_of_int xs) ^ "]"
;;

let test_cases = [
  [];
  [1];
  [2; 1];
  [3; 1; 2];
  [5; 4; 3; 2; 1];
  [1; 2; 3; 4; 5];
  [3; 1; 3; 2; 1];
  [-1; 3; 0; -5; 2];
];;

let assert_counted_sorted label input (count : int) actual =
  let expected = List.sort compare input in
  if actual <> expected then
    Printf.printf "NG %s %s: expected sorted list %s but got %s\n"
      label (show_int_list input) (show_int_list expected) (show_int_list actual)
  else if List.length input <= 1 && count < 0 then
    Printf.printf "NG %s %s: comparison count must be >= 0 but got %d\n"
      label (show_int_list input) count
  else if List.length input >= 2 && count <= 0 then
    Printf.printf "NG %s %s: comparison count must be > 0 for non-trivial input but got %d\n"
      label (show_int_list input) count
  else
    print_endline ("OK " ^ label ^ " " ^ show_int_list input)
;;

List.iter
  (fun input ->
     let (count, sorted) = {function_name} input in
     assert_counted_sorted "{function_name}" input count sorted)
  test_cases;;
'''


def make_test(question, name, ocaml_code):
    return {
        "question": str(question),
        "name": name,
        "code": ocaml_code,
    }


def make_sort_test(question, function_name):
    return make_test(
        question,
        function_name,
        SORT_TEST_CODE_TEMPLATE.replace("{function_name}", function_name),
    )


def make_count_sort_test(question, function_name):
    return make_test(
        question,
        function_name,
        COUNT_SORT_TEST_CODE_TEMPLATE.replace("{function_name}", function_name),
    )


TESTS = [
    make_sort_test("1", "exchange_sort"),
    make_sort_test("1", "selection_sort"),
    make_sort_test("1", "insertion_sort"),
    make_sort_test("2", "merge_sort"),
    make_sort_test("2", "quick_sort"),
    make_count_sort_test("3-1", "exchange_sort_c"),
    make_count_sort_test("3-1", "selection_sort_c"),
    make_count_sort_test("3-1", "insertion_sort_c"),
    make_count_sort_test("3-2", "merge_sort_c"),
    make_count_sort_test("3-2", "quick_sort_c"),
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
        + "(* ---- second period week3 sorting checker test ---- *)\n"
        + test_code
        + "\n"
    )


def run_one_test(ml_file, test):
    student_code = read_file_text(ml_file)
    script = build_ocaml_script(student_code, test["code"])

    result = {
        "question": str(test["question"]),
        "test": test["name"],
        "status": "ERROR",
        "stdout": "",
        "stderr": "",
    }

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".ml",
            encoding="utf-8",
            delete=False,
        ) as f:
            f.write(script)
            temp_path = f.name

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

        ok_lines = [line for line in stdout.splitlines() if line.startswith("OK ")]

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

    except Exception as e:
        result["status"] = "ERROR"
        result["stderr"] = repr(e)
        return result

    finally:
        if temp_path:
            try:
                Path(temp_path).unlink()
            except Exception:
                pass


def question_sort_key(question):
    order = {"1": 1, "2": 2, "3-1": 3, "3-2": 4}
    question = str(question)
    if question in order:
        return [order[question]]

    parts = question.split("-")
    key = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part)
    return key


def summarize_by_question(file_results):
    grouped = {}

    for result in file_results:
        question = str(result.get("question", ""))
        grouped.setdefault(question, []).append(result)

    summaries = []

    for question in sorted(grouped.keys(), key=question_sort_key):
        question_results = grouped[question]
        statuses = [r.get("status") for r in question_results]

        # Week 3 questions are choice-based: one correctly implemented candidate
        # is enough for the whole question, even if other candidates are undefined.
        if "OK" in statuses:
            status = "OK"
        elif "NG" in statuses:
            status = "NG"
        elif "WARNING" in statuses:
            status = "WARNING"
        else:
            status = "ERROR"

        summaries.append({
            "question": question,
            "status": status,
            "results": question_results,
        })

    return summaries
