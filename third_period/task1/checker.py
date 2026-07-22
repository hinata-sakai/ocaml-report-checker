# -*- coding: utf-8 -*-

"""Automatic checker for third-period task 1 (custom polymorphic lists)."""

import re
import subprocess
import tempfile
from pathlib import Path


OCAML_COMMAND = "ocaml"
TIMEOUT_SECONDS = 8
REQUIRED_FUNCTIONS = {
    "create", "unshift", "shift", "push", "pop", "size", "max", "min",
    "get", "indexOf", "set", "remove", "concat",
}


def make_test(question, code):
    return {"question": question, "name": question, "code": code}


PRELUDE = r'''
open List;;
let rec to_builtin_list xs =
  match xs with Nil -> [] | Cell (x, rest) -> x :: to_builtin_list rest
;;
let pass label condition =
  if condition then print_endline ("OK " ^ label)
  else print_endline ("NG " ^ label)
;;
'''


TESTS = [
    make_test("create", PRELUDE + 'pass "create" (to_builtin_list (create ()) = []);;'),
    make_test("unshift", PRELUDE + 'pass "unshift" (to_builtin_list (unshift 10 Nil) = [10]);;'),
    make_test("shift", PRELUDE + 'pass "shift" (to_builtin_list (shift (Cell (10, Cell (2, Cell (5, Cell (8, Cell (12, Cell (2, Cell (1, Nil))))))))) = [2;5;8;12;2;1]);;'),
    make_test("push", PRELUDE + 'pass "push" (to_builtin_list (push 8 Nil) = [8]);;'),
    make_test("pop", PRELUDE + 'pass "pop" (to_builtin_list (pop (Cell (10, Cell (2, Cell (5, Cell (8, Cell (12, Cell (2, Cell (1, Nil))))))))) = [10;2;5;8;12;2]);;'),
    make_test("size", PRELUDE + 'pass "size l" (size (Cell (10, Cell (2, Cell (5, Cell (8, Cell (12, Cell (2, Cell (1, Nil))))))))) = 7);; pass "size l2" (size (Cell (12, Cell (2, Cell (1, Nil))))) = 3);;'),
    make_test("max", PRELUDE + 'pass "max" (max (Cell (12, Cell (2, Cell (1, Nil)))) = 12);;'),
    make_test("min", PRELUDE + 'pass "min" (min (Cell (12, Cell (2, Cell (1, Nil)))) = 1);;'),
    make_test("get", PRELUDE + 'pass "get" (get 3 (Cell (10, Cell (2, Cell (5, Cell (8, Cell (12, Cell (2, Cell (1, Nil))))))))) = 8);;'),
    make_test("indexOf", PRELUDE + 'let l = Cell (10, Cell (2, Cell (5, Cell (8, Cell (12, Cell (2, Cell (1, Nil))))))) in pass "indexOf existing" (indexOf 12 l = 4); pass "indexOf missing" (indexOf 99 l = -1); pass "indexOf first" (indexOf 2 l = 1);;'),
    make_test("set", PRELUDE + 'let l = Cell (10, Cell (2, Cell (5, Cell (8, Cell (12, Cell (2, Cell (1, Nil))))))) in pass "set one" (to_builtin_list (set 1 0 l) = [10;2;5;8;12;2;0]); pass "set all" (to_builtin_list (set 2 99 l) = [10;99;5;8;12;99;1]);;'),
    make_test("remove", PRELUDE + 'let l = Cell (10, Cell (2, Cell (5, Cell (8, Cell (12, Cell (2, Cell (1, Nil))))))) in pass "remove one" (to_builtin_list (remove 5 l) = [10;2;8;12;2;1]); pass "remove all" (to_builtin_list (remove 2 l) = [10;5;8;12;1]);;'),
    make_test("concat", PRELUDE + 'let l1 = Cell (10, Cell (2, Cell (5, Cell (8, Nil)))) in let l2 = Cell (12, Cell (2, Cell (1, Nil))) in pass "concat" (to_builtin_list (concat l1 l2) = [10;2;5;8;12;2;1]);;'),
    {"question": "extra", "name": "extra", "extra": True, "code": ""},
]


def read_file_text(path):
    return Path(path).read_text(encoding="utf-8", errors="replace")


def count_extra_functions(code):
    """Count additional ``let`` bindings in List (up to two for scoring)."""
    code = re.sub(r"\(\*.*?\*\)", "", code, flags=re.DOTALL)
    match = re.search(r"\bmodule\s+List\s*=\s*struct\b(.*?)\bend\b", code, re.DOTALL)
    body = match.group(1) if match else code
    bindings = re.findall(
        r"(?m)^(?P<indent>[ \t]*)let\s+(?:rec\s+)?(?P<name>[a-zA-Z_][\w']*)\b",
        body,
    )
    required_indents = [len(indent.expandtabs(8)) for indent, name in bindings
                        if name in REQUIRED_FUNCTIONS]
    top_indent = min(required_indents) if required_indents else 0
    names = {name for indent, name in bindings if len(indent.expandtabs(8)) == top_indent}
    return min(2, len(names - REQUIRED_FUNCTIONS))


def run_one_test(ml_file, test):
    result = {"question": test["question"], "test": test["name"],
              "status": "ERROR", "stdout": "", "stderr": ""}
    student_code = read_file_text(ml_file)
    if test.get("extra"):
        count = count_extra_functions(student_code)
        result.update(status="OK", stdout="OK extra\n", extra_points=count * 2)
        return result

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ml", encoding="utf-8", delete=False) as file:
            file.write(student_code + "\n(* ---- third period task1 test ---- *)\n" + test["code"] + "\n")
            temp_path = file.name
        completed = subprocess.run([OCAML_COMMAND, temp_path], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, timeout=TIMEOUT_SECONDS)
        result["stdout"], result["stderr"] = completed.stdout or "", completed.stderr or ""
        if completed.returncode != 0:
            return result
        if "NG " in result["stdout"] or not any(
                line.startswith("OK ") for line in result["stdout"].splitlines()):
            result["status"] = "NG"
        elif result["stderr"].strip():
            result["status"] = "WARNING"
        else:
            result["status"] = "OK"
        return result
    except subprocess.TimeoutExpired:
        result["stderr"] = "Timeout: 再帰が止まらない、または実行に時間がかかりすぎています。"
        return result
    except Exception as exc:
        result["stderr"] = repr(exc)
        return result
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


def summarize_by_question(file_results):
    summaries = []
    for result in file_results:
        summary = {"question": result["question"], "status": result["status"], "results": [result]}
        if result["question"] == "extra":
            summary["extra_points"] = result.get("extra_points", 0)
        summaries.append(summary)
    return summaries
