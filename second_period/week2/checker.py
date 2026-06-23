# -*- coding: utf-8 -*-

"""Checker for OCaml second period, week 2.

Targets:
- Q1-1 diff_forward    : (float -> float) -> float -> float
- Q1-2 diff_central    : (float -> float) -> float -> float
- Q1-4 ext             : (float -> float) -> float -> (float * float)
- Q2-1-1 area_rectangle: (float -> float) -> float -> float -> float
- Q2-1-2 area_trapezoid: (float -> float) -> float -> float -> float
- Q2-3 area_simpson    : (float -> float) -> float -> float -> float
- Q2-4 integral        : ((float -> float) -> float -> float -> float) ->
                         (float -> float) -> float -> float -> float

Notes:
- Floating-point answers are graded with approximate comparisons.
- The assignment expects h, c, and dx to be global values in student code.
- Research and discussion sections should be checked manually from the PDF.
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
        "diff_forward",
        r'''
let approx_equal eps actual expected =
  abs_float (actual -. expected) <= eps
;;

let assert_approx label actual expected eps =
  if approx_equal eps actual expected then
    print_endline ("OK " ^ label)
  else
    Printf.printf "NG %s: expected %.12g but got %.12g (eps %.12g)\n" label expected actual eps
;;

assert_approx "diff_forward (fun x -> x *. x) 2.0" (diff_forward (fun x -> x *. x) 2.0) 4.0 1e-3;;
assert_approx "diff_forward (fun x -> x *. x *. x) 2.0" (diff_forward (fun x -> x *. x *. x) 2.0) 12.0 1e-3;;
assert_approx "diff_forward sin 0.0" (diff_forward sin 0.0) 1.0 1e-3;;
''',
    ),
    make_test(
        "1-2",
        "diff_central",
        r'''
let approx_equal eps actual expected =
  abs_float (actual -. expected) <= eps
;;

let assert_approx label actual expected eps =
  if approx_equal eps actual expected then
    print_endline ("OK " ^ label)
  else
    Printf.printf "NG %s: expected %.12g but got %.12g (eps %.12g)\n" label expected actual eps
;;

assert_approx "diff_central (fun x -> x *. x) 2.0" (diff_central (fun x -> x *. x) 2.0) 4.0 1e-3;;
assert_approx "diff_central (fun x -> x *. x *. x) 2.0" (diff_central (fun x -> x *. x *. x) 2.0) 12.0 1e-3;;
assert_approx "diff_central sin 0.0" (diff_central sin 0.0) 1.0 1e-3;;
''',
    ),
    make_test(
        "1-4",
        "ext",
        r'''
let approx_equal eps actual expected =
  abs_float (actual -. expected) <= eps
;;

let assert_approx label actual expected eps =
  if approx_equal eps actual expected then
    print_endline ("OK " ^ label)
  else
    Printf.printf "NG %s: expected %.12g but got %.12g (eps %.12g)\n" label expected actual eps
;;

let check_ext label f start expected_x expected_y =
  let (actual_x, actual_y) = ext f start in
  assert_approx (label ^ " x") actual_x expected_x 1e-2;
  assert_approx (label ^ " f(x)") actual_y expected_y 1e-2
;;

check_ext "ext (fun x -> (x -. 2.0) *. (x -. 2.0)) 0.0" (fun x -> (x -. 2.0) *. (x -. 2.0)) 0.0 2.0 0.0;;
check_ext "ext (fun x -> (x +. 1.0) *. (x +. 1.0)) 1.0" (fun x -> (x +. 1.0) *. (x +. 1.0)) 1.0 (-1.0) 0.0;;
''',
    ),
    make_test(
        "2-1-1",
        "area_rectangle",
        r'''
let approx_equal eps actual expected =
  abs_float (actual -. expected) <= eps
;;

let assert_approx label actual expected eps =
  if approx_equal eps actual expected then
    print_endline ("OK " ^ label)
  else
    Printf.printf "NG %s: expected %.12g but got %.12g (eps %.12g)\n" label expected actual eps
;;

assert_approx "area_rectangle (fun x -> x) 0.0 0.1" (area_rectangle (fun x -> x) 0.0 0.1) 0.0 1e-3;;
assert_approx "area_rectangle (fun x -> x) 2.0 0.5" (area_rectangle (fun x -> x) 2.0 0.5) 1.0 1e-3;;
assert_approx "area_rectangle (fun x -> x *. x) 2.0 0.5" (area_rectangle (fun x -> x *. x) 2.0 0.5) 2.0 1e-3;;
''',
    ),
    make_test(
        "2-1-2",
        "area_trapezoid",
        r'''
let approx_equal eps actual expected =
  abs_float (actual -. expected) <= eps
;;

let assert_approx label actual expected eps =
  if approx_equal eps actual expected then
    print_endline ("OK " ^ label)
  else
    Printf.printf "NG %s: expected %.12g but got %.12g (eps %.12g)\n" label expected actual eps
;;

assert_approx "area_trapezoid (fun x -> x) 0.0 0.1" (area_trapezoid (fun x -> x) 0.0 0.1) 0.005 1e-3;;
assert_approx "area_trapezoid (fun x -> x) 2.0 0.5" (area_trapezoid (fun x -> x) 2.0 0.5) 1.125 1e-3;;
assert_approx "area_trapezoid (fun x -> x *. x) 2.0 0.5" (area_trapezoid (fun x -> x *. x) 2.0 0.5) 2.5625 1e-3;;
''',
    ),
    make_test(
        "2-3",
        "area_simpson",
        r'''
let approx_equal eps actual expected =
  abs_float (actual -. expected) <= eps
;;

let assert_approx label actual expected eps =
  if approx_equal eps actual expected then
    print_endline ("OK " ^ label)
  else
    Printf.printf "NG %s: expected %.12g but got %.12g (eps %.12g)\n" label expected actual eps
;;

assert_approx "area_simpson (fun x -> x) 0.0 0.1" (area_simpson (fun x -> x) 0.0 0.1) 0.005 1e-3;;
assert_approx "area_simpson (fun x -> x *. x) 0.0 0.1" (area_simpson (fun x -> x *. x) 0.0 0.1) 0.000333333333 1e-3;;
assert_approx "area_simpson (fun x -> x *. x) 2.0 0.5" (area_simpson (fun x -> x *. x) 2.0 0.5) 2.5416666667 1e-3;;
''',
    ),
    make_test(
        "2-4",
        "integral",
        r'''
let approx_equal eps actual expected =
  abs_float (actual -. expected) <= eps
;;

let assert_approx label actual expected eps =
  if approx_equal eps actual expected then
    print_endline ("OK " ^ label)
  else
    Printf.printf "NG %s: expected %.12g but got %.12g (eps %.12g)\n" label expected actual eps
;;

let pi = 4.0 *. atan 1.0;;

assert_approx "integral area_rectangle (fun x -> x) 0.0 1.0" (integral area_rectangle (fun x -> x) 0.0 1.0) 0.5 1e-2;;
assert_approx "integral area_trapezoid (fun x -> x) 0.0 1.0" (integral area_trapezoid (fun x -> x) 0.0 1.0) 0.5 1e-2;;
assert_approx "integral area_simpson (fun x -> x *. x) 0.0 1.0" (integral area_simpson (fun x -> x *. x) 0.0 1.0) (1.0 /. 3.0) 1e-2;;
assert_approx "integral area_simpson sin 0.0 pi" (integral area_simpson sin 0.0 pi) 2.0 1e-2;;
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
        + "(* ---- second period week2 checker test ---- *)\n"
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