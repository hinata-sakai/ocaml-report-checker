# -*- coding: utf-8 -*-

"""Automatic checker for third-period task 4 (the ``Bag`` module)."""

import re
import subprocess
import tempfile
from pathlib import Path


OCAML_COMMAND = "ocaml"
TIMEOUT_SECONDS = 8
QUESTION_ORDER = [
    "create", "is_empty", "insert", "is_element", "count", "search",
    "delete", "delete_all", "to_list", "union",
]


def make_test(question, code, challenge=False, hidden_name=None):
    return {"question": question, "name": question, "code": code,
            "challenge": challenge, "hidden_name": hidden_name}


PRELUDE = r'''
open Bag;;
let pass label condition =
  if condition then print_endline ("OK " ^ label)
  else print_endline ("NG " ^ label)
;;
'''

BAG = r'''
let b0 = create ();;
let b1 = insert "apple" b0;;
let b2 = insert "apple" b1;;
let b3 = insert "banana" b2;;
'''

TESTS = [
    make_test("create", PRELUDE + r'''
let empty = create ();;
pass "create empty" (is_empty empty);;
'''),
    make_test("is_empty", PRELUDE + r'''
let empty = create ();;
let nonempty = insert "apple" empty;;
pass "empty after create" (is_empty empty);;
pass "nonempty after insert" (not (is_empty nonempty));;
'''),
    make_test("insert", PRELUDE + BAG + r'''
pass "insert counts" (count "apple" b3 = 2 && count "banana" b3 = 1);;
'''),
    make_test("is_element", PRELUDE + BAG + r'''
pass "present elements" (is_element "apple" b3 && is_element "banana" b3);;
pass "absent element" (not (is_element "orange" b3));;
'''),
    make_test("count", PRELUDE + BAG + r'''
pass "counts" (count "apple" b3 = 2 && count "banana" b3 = 1 &&
               count "orange" b3 = 0);;
'''),
    make_test("search", PRELUDE + BAG + r'''
pass "search through public operations"
  (is_element "apple" b3 && not (is_element "orange" b3) &&
   count "apple" b3 = 2 && count "orange" b3 = 0);;
''', hidden_name="search"),
    make_test("delete", PRELUDE + BAG + r'''
let b4 = delete "apple" b3;;
let b5 = delete "apple" b4;;
let b6 = delete "missing" b5;;
pass "delete one" (count "apple" b4 = 1);;
pass "delete last" (count "apple" b5 = 0 && not (is_element "apple" b5));;
pass "delete absent" (count "banana" b6 = 1);;
'''),
    make_test("delete_all", PRELUDE + r'''
let one = insert "apple" (create ());;
let removed = delete "apple" one;;
pass "delete last through delete"
  (count "apple" removed = 0 && not (is_element "apple" removed) &&
   is_empty removed);;
''', hidden_name="delete_all"),
    make_test("to_list", PRELUDE + BAG + r'''
pass "flat list"
  (List.sort compare (to_list b3) = ["apple"; "apple"; "banana"]);;
''', challenge=True),
    make_test("union", PRELUDE + BAG + r'''
let b_heavy = insert "banana" (insert "orange" (create ()));;
let b_mixed = union b3 b_heavy;;
pass "union counts"
  (count "apple" b_mixed = 2 && count "banana" b_mixed = 2 &&
   count "orange" b_mixed = 1);;
''', challenge=True),
]


def read_file_text(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return Path(path).read_text(encoding="utf-8", errors="replace")


def _masked_code(code):
    """Mask nested comments and strings, retaining offsets for extraction."""
    result = list(code)
    i, comment_depth, in_string = 0, 0, False
    while i < len(code):
        if comment_depth:
            if code.startswith("(*", i):
                comment_depth += 1
                result[i:i + 2] = "  "
                i += 2
            elif code.startswith("*)", i):
                comment_depth -= 1
                result[i:i + 2] = "  "
                i += 2
            else:
                if code[i] != "\n":
                    result[i] = " "
                i += 1
        elif in_string:
            if code[i] == "\\" and i + 1 < len(code):
                result[i:i + 2] = "  "
                i += 2
            else:
                if code[i] == '"':
                    in_string = False
                if code[i] != "\n":
                    result[i] = " "
                i += 1
        elif code.startswith("(*", i):
            comment_depth = 1
            result[i:i + 2] = "  "
            i += 2
        elif code[i] == '"':
            in_string = True
            result[i] = " "
            i += 1
        else:
            i += 1
    return "".join(result)


MODULE_PATTERN = re.compile(
    r"\bmodule\s+Bag\b(?:(?!\bstruct\b).)*=\s*struct\b", re.S)


def extract_bag_module_code(code):
    """Extract Bag and its named module type, dropping trailing examples."""
    masked = _masked_code(code)
    match = MODULE_PATTERN.search(masked)
    if not match:
        return code
    start = match.start()
    header = masked[match.start():match.end()]
    named = re.search(r"\bBag\s*:\s*([A-Z][A-Za-z0-9_']*)\s*=", header)
    if named:
        declarations = list(re.finditer(
            r"\bmodule\s+type\s+" + re.escape(named.group(1)) + r"\b",
            masked[:start]))
        if declarations:
            start = declarations[-1].start()

    depth, pos = 1, match.end()
    tokens = re.compile(r"\b(struct|sig|end)\b")
    while depth:
        token = tokens.search(masked, pos)
        if not token:
            return code[start:]
        depth += 1 if token.group(1) in ("struct", "sig") else -1
        pos = token.end()
    end = pos
    while end < len(code) and code[end].isspace():
        end += 1
    if code.startswith(";;", end):
        end += 2
    return code[start:end]


def _defines_challenge_function(code, name):
    masked = _masked_code(code)
    return any(re.search(pattern + re.escape(name) + r"\b", masked) for pattern in
               (r"\blet\s+rec\s+", r"\blet\s+", r"\bval\s+"))


def _execute(script):
    path = None
    try:
        with tempfile.NamedTemporaryFile(
                "w", suffix=".ml", encoding="utf-8", delete=False) as file:
            file.write(script)
            path = file.name
        return subprocess.run(
            [OCAML_COMMAND, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=TIMEOUT_SECONDS)
    finally:
        if path:
            try:
                Path(path).unlink()
            except OSError:
                pass


def _binding_is_exported(module_code, name):
    probe = module_code + "\nopen Bag;;\nlet _ = " + name + ";;\n"
    try:
        completed = _execute(probe)
    except (subprocess.TimeoutExpired, OSError):
        return None
    if completed.returncode == 0:
        return True
    if re.search(r"Unbound value\s+" + re.escape(name) + r"\b", completed.stderr or ""):
        return False
    return None


def run_one_test(ml_file, test):
    result = {"question": test["question"], "test": test["name"],
              "status": "ERROR", "stdout": "", "stderr": ""}
    student_code = read_file_text(ml_file)
    module_code = extract_bag_module_code(student_code)
    try:
        completed = _execute(module_code + "\n" + test["code"] + "\n")
        result["stdout"], result["stderr"] = completed.stdout or "", completed.stderr or ""
        if completed.returncode != 0:
            return result
        if "NG " in result["stdout"] or not any(
                line.startswith("OK ") for line in result["stdout"].splitlines()):
            result["status"] = "NG"
            return result
        hidden_name = test.get("hidden_name")
        if hidden_name and _binding_is_exported(module_code, hidden_name) is not False:
            result["status"] = "NG"
            result["stderr"] += ("\n{} はモジュール外から参照できないよう"
                                 "隠蔽してください。").format(hidden_name)
            return result
        result["status"] = "WARNING" if result["stderr"].strip() else "OK"
    except subprocess.TimeoutExpired:
        result["stderr"] = "Timeout: 実行に時間がかかりすぎています。"
    except Exception as exc:
        result["stderr"] = repr(exc)
    return result


def question_sort_key(question):
    question = str(question)
    return (QUESTION_ORDER.index(question), "") if question in QUESTION_ORDER else (99, question)


def summarize_by_question(file_results):
    summaries = []
    for question in sorted({r["question"] for r in file_results}, key=question_sort_key):
        results = [r for r in file_results if r["question"] == question]
        statuses = [r["status"] for r in results]
        status = ("ERROR" if "ERROR" in statuses else "NG" if "NG" in statuses else
                  "WARNING" if "WARNING" in statuses else "OK")
        summaries.append({"question": question, "status": status, "results": results})
    return summaries


def run_checker(ml_file):
    student_code = read_file_text(ml_file)
    masked = _masked_code(student_code)
    has_bag = MODULE_PATTERN.search(masked) is not None
    module_code = extract_bag_module_code(student_code)

    selected = [test for test in TESTS if not test["challenge"]]

    for test in (test for test in TESTS if test["challenge"]):
        name = test["question"]

        if has_bag:
            implemented = (
                _binding_is_exported(module_code, name) is True
                or _defines_challenge_function(student_code, name)
            )
        else:
            implemented = _defines_challenge_function(student_code, name)

        if implemented:
            selected.append(test)

    return [run_one_test(ml_file, test) for test in selected]
