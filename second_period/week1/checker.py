# -*- coding: utf-8 -*-

"""Checker for OCaml second period, week 1.

Targets:
- Q1-1 count_ones      : int -> int
- Q2-1 power_val       : int -> int
- Q2-2 power_steps     : int -> int
- Q3-1 collatz_steps   : int -> int
- Q3-2 collatz_path    : int -> int list

Notes:
- power_val is graded as one-argument function based on the assignment text.
- power_steps is graded as one-argument function.
- power_steps accepts both n and n + 1 because recursion-count interpretation may differ.
- collatz_steps accepts both operation count and operation count + 1 for the same reason.
- Explanation and discussion sections should be checked manually from the PDF.
"""

import subprocess
import tempfile
from pathlib import Path


OCAML_COMMAND = "ocaml"
TIMEOUT_SECONDS = 8


def make_test(question, name, ocaml_code):
    return {
        "question": str(question),
        "name": name,
        "code": ocaml_code,
    }


TESTS = [
    make_test(
        "1-1",
        "count_ones",
        r'''
let assert_eq label actual expected =
  if actual = expected then
    print_endline ("OK " ^ label)
  else
    Printf.printf "NG %s: expected %d but got %d\n" label expected actual
;;

assert_eq "count_ones 1" (count_ones 1) 1;;
assert_eq "count_ones 2" (count_ones 2) 1;;
assert_eq "count_ones 3" (count_ones 3) 2;;
assert_eq "count_ones 7" (count_ones 7) 3;;
assert_eq "count_ones 8" (count_ones 8) 1;;
assert_eq "count_ones 10" (count_ones 10) 2;;
assert_eq "count_ones 100" (count_ones 100) 3;;
''',
    ),
    make_test(
        "2-1",
        "power_val",
        r'''
let assert_eq label actual expected =
  if actual = expected then
    print_endline ("OK " ^ label)
  else
    Printf.printf "NG %s: expected %d but got %d\n" label expected actual
;;

assert_eq "power_val 1" (power_val 1) 1;;
assert_eq "power_val 2" (power_val 2) 4;;
assert_eq "power_val 3" (power_val 3) 27;;
assert_eq "power_val 4" (power_val 4) 256;;
assert_eq "power_val 5" (power_val 5) 3125;;
assert_eq "power_val 7" (power_val 7) 823543;;
''',
    ),
    make_test(
        "2-2",
        "power_steps",
        r'''
let assert_steps label n actual =
  if actual = n || actual = n + 1 then
    print_endline ("OK " ^ label)
  else
    Printf.printf "NG %s: expected %d or %d but got %d\n" label n (n + 1) actual
;;

assert_steps "power_steps 1" 1 (power_steps 1);;
assert_steps "power_steps 2" 2 (power_steps 2);;
assert_steps "power_steps 3" 3 (power_steps 3);;
assert_steps "power_steps 7" 7 (power_steps 7);;
assert_steps "power_steps 10" 10 (power_steps 10);;
''',
    ),
    make_test(
        "3-1",
        "collatz_steps",
        r'''
    let assert_steps label expected actual =
    if actual = expected || actual = expected + 1 then
        print_endline ("OK " ^ label)
    else
        Printf.printf "NG %s: expected %d or %d but got %d\n" label expected (expected + 1) actual
    ;;

    assert_steps "collatz_steps 1" 0 (collatz_steps 1);;
    assert_steps "collatz_steps 2" 1 (collatz_steps 2);;
    assert_steps "collatz_steps 3" 7 (collatz_steps 3);;
    assert_steps "collatz_steps 4" 2 (collatz_steps 4);;
    assert_steps "collatz_steps 5" 5 (collatz_steps 5);;
    assert_steps "collatz_steps 7" 16 (collatz_steps 7);;
    assert_steps "collatz_steps 8" 3 (collatz_steps 8);;
    assert_steps "collatz_steps 9" 19 (collatz_steps 9);;
    assert_steps "collatz_steps 10" 6 (collatz_steps 10);;
    ''',
    ),
    make_test(
        "3-2",
        "collatz_path",
        r'''
let rec string_of_int_list xs =
  match xs with
  | [] -> "[]"
  | _ ->
      let rec inner ys =
        match ys with
        | [] -> ""
        | [z] -> string_of_int z
        | z :: zs -> string_of_int z ^ "; " ^ inner zs
      in
      "[" ^ inner xs ^ "]"
;;

let assert_list_eq label actual expected =
  if actual = expected then
    print_endline ("OK " ^ label)
  else
    Printf.printf
      "NG %s: expected %s but got %s\n"
      label
      (string_of_int_list expected)
      (string_of_int_list actual)
;;

assert_list_eq "collatz_path 1" (collatz_path 1) [1];;
assert_list_eq "collatz_path 2" (collatz_path 2) [2; 1];;
assert_list_eq "collatz_path 3" (collatz_path 3) [3; 10; 5; 16; 8; 4; 2; 1];;
assert_list_eq "collatz_path 6" (collatz_path 6) [6; 3; 10; 5; 16; 8; 4; 2; 1];;
assert_list_eq "collatz_path 7" (collatz_path 7) [7; 22; 11; 34; 17; 52; 26; 13; 40; 20; 10; 5; 16; 8; 4; 2; 1];;
assert_list_eq "collatz_path 9" (collatz_path 9) [9; 28; 14; 7; 22; 11; 34; 17; 52; 26; 13; 40; 20; 10; 5; 16; 8; 4; 2; 1];;
assert_list_eq "collatz_path 10" (collatz_path 10) [10; 5; 16; 8; 4; 2; 1];;
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
        + "(* ---- second period week1 checker test ---- *)\n"
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
    parts = str(question).split("-")

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
            "results": question_results,
        })

    return summaries