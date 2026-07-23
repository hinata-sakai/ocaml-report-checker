# -*- coding: utf-8 -*-

"""Automatic checker for third-period task 3 (the ``BTree`` module)."""

import re
import subprocess
import tempfile
from pathlib import Path


OCAML_COMMAND = "ocaml"
TIMEOUT_SECONDS = 8
QUESTION_ORDER = [
    "create", "insert", "search", "search_min", "delete_min", "delete",
    "dfs", "bfs",
]


def make_test(question, code, challenge=False, hidden_name=None):
    return {
        "question": question,
        "name": question,
        "code": code,
        "challenge": challenge,
        "hidden_name": hidden_name,
    }


PRELUDE = r'''
open BTree;;
let pass label condition =
  if condition then print_endline ("OK " ^ label)
  else print_endline ("NG " ^ label)
;;
'''

TREE = r'''
let t0 = create ();;
let t1 = insert 5 t0;;
let t2 = insert 3 t1;;
let t3 = insert 7 t2;;
'''

DELETE_TREE = r'''
let d0 = create ();;
let d1 = insert 5 d0;;
let d2 = insert 3 d1;;
let d3 = insert 7 d2;;
let d4 = insert 2 d3;;
let d5 = insert 4 d4;;
let d6 = insert 6 d5;;
let d7 = insert 8 d6;;
let removed_root = delete 5 d7;;
'''

TESTS = [
    make_test("create", PRELUDE + r'''
let empty = create ();;
pass "create empty" (not (search 1 empty));;
'''),
    make_test("insert", PRELUDE + TREE + r'''
pass "insert values" (search 5 t3 && search 3 t3 && search 7 t3);;
'''),
    make_test("search", PRELUDE + TREE + r'''
pass "search present" (search 3 t3 && search 5 t3 && search 7 t3);;
pass "search absent" (not (search 2 t3) && not (search 9 t3));;
'''),
    make_test("search_min", PRELUDE + DELETE_TREE + r'''
pass "successor after two-child deletion"
  (not (search 5 removed_root) && search 2 removed_root && search 3 removed_root &&
   search 4 removed_root && search 6 removed_root && search 7 removed_root &&
   search 8 removed_root);;
''', hidden_name="search_min"),
    make_test("delete_min", PRELUDE + DELETE_TREE + r'''
pass "minimum removed exactly once"
  (not (search 5 removed_root) && search 6 removed_root && search 7 removed_root &&
   search 8 removed_root);;
''', hidden_name="delete_min"),
    make_test("delete", PRELUDE + DELETE_TREE + r'''
let leaf = delete 2 d7;;
let one_child_source = insert 1 d7;;
let one_child = delete 2 one_child_source;;
pass "delete leaf" (not (search 2 leaf) && search 3 leaf);;
pass "delete one child" (not (search 2 one_child) && search 1 one_child);;
pass "delete two children"
  (not (search 5 removed_root) && search 3 removed_root && search 7 removed_root);;
'''),
    make_test("dfs", PRELUDE + DELETE_TREE + r'''
pass "dfs preorder" (dfs d7 = [5; 3; 2; 4; 7; 6; 8]);;
''', challenge=True),
    make_test("bfs", PRELUDE + DELETE_TREE + r'''
pass "bfs level order" (bfs d7 = [5; 3; 7; 2; 4; 6; 8]);;
''', challenge=True),
]


def read_file_text(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return Path(path).read_text(encoding="utf-8", errors="replace")


def _masked_code(code):
    """Replace comments and strings with spaces while preserving positions."""
    result = list(code)
    i = 0
    comment_depth = 0
    in_string = False
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


def extract_btree_module_code(code):
    """Extract BTree (and a preceding named signature), excluding examples."""
    masked = _masked_code(code)
    match = re.search(r"\bmodule\s+BTree\b(?:(?!\bstruct\b).)*=\s*struct\b", masked, re.S)
    if not match:
        return code

    start = match.start()
    header = masked[match.start():match.end()]
    # ``module BTree : BTREE`` needs its module type declaration as well.
    named = re.search(r"\bBTree\s*:\s*([A-Z][A-Za-z0-9_']*)\s*=", header)
    if named:
        declarations = list(re.finditer(
            r"\bmodule\s+type\s+" + re.escape(named.group(1)) + r"\b", masked[:start]
        ))
        if declarations:
            start = declarations[-1].start()

    depth = 1
    pos = match.end()
    tokens = re.compile(r"\b(struct|sig|end)\b")
    while depth:
        token = tokens.search(masked, pos)
        if not token:
            return code[start:]
        depth += 1 if token.group(1) in ("struct", "sig") else -1
        pos = token.end()
    whitespace_end = pos
    while whitespace_end < len(code) and code[whitespace_end].isspace():
        whitespace_end += 1
    if code.startswith(";;", whitespace_end):
        whitespace_end += 2
    return code[start:whitespace_end]

def _defines_challenge_function(student_code, name):
    """Return True when the submitted source appears to define dfs/bfs."""
    masked = _masked_code(student_code)

    patterns = [
        r"\blet\s+rec\s+" + re.escape(name) + r"\b",
        r"\blet\s+" + re.escape(name) + r"\b",
        r"\bval\s+" + re.escape(name) + r"\b",
    ]

    return any(re.search(pattern, masked) for pattern in patterns)

def build_ocaml_script(student_code, test_code):
    return extract_btree_module_code(student_code) + "\n" + test_code + "\n"


def _execute(script):
    path = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".ml", encoding="utf-8", delete=False) as f:
            f.write(script)
            path = f.name
        return subprocess.run(
            [OCAML_COMMAND, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=TIMEOUT_SECONDS,
        )
    finally:
        if path:
            try:
                Path(path).unlink()
            except OSError:
                pass


def _is_exported(module_code, name):
    probe = module_code + "\nopen BTree;;\nlet _ = " + name + " (create ());;\n"
    try:
        completed = _execute(probe)
    except (subprocess.TimeoutExpired, OSError):
        return None
    if completed.returncode == 0:
        return True
    if re.search(r"Unbound value\s+" + re.escape(name) + r"\b", completed.stderr):
        return False
    return None


def _is_challenge_exported(module_code, name):
    """Return whether an optional challenge binding is exposed by ``BTree``."""
    probe = module_code + "\nopen BTree;;\nlet _ = " + name + ";;\n"
    try:
        completed = _execute(probe)
    except (subprocess.TimeoutExpired, OSError):
        return False

    if completed.returncode == 0:
        return True

    stderr = completed.stderr or ""

    # BTree モジュール自体がない場合は、dfs/bfs は未実装扱いにする
    if re.search(r"Unbound module\s+BTree\b", stderr):
        return False

    # dfs / bfs がない場合も、未実装扱いにする
    if re.search(r"Unbound value\s+" + re.escape(name) + r"\b", stderr):
        return False

    # 存在確認中に別のエラーが出た場合も、チャレンジ実装済みとはみなさない
    return False


def run_one_test(ml_file, test):
    result = {"question": test["question"], "test": test["name"],
              "status": "ERROR", "stdout": "", "stderr": ""}
    student_code = read_file_text(ml_file)
    module_code = extract_btree_module_code(student_code)
    try:
        completed = _execute(build_ocaml_script(student_code, test["code"]))
        result["stdout"], result["stderr"] = completed.stdout or "", completed.stderr or ""
        if completed.returncode != 0:
            return result
        if "NG " in result["stdout"] or not any(
                line.startswith("OK ") for line in result["stdout"].splitlines()):
            result["status"] = "NG"
            return result
        hidden_name = test.get("hidden_name")
        if hidden_name and _is_exported(module_code, hidden_name) is not False:
            result["status"] = "NG"
            result["stderr"] += "\n{} はモジュール外から参照できないよう隠蔽してください。".format(hidden_name)
            return result
        result["status"] = "WARNING" if result["stderr"].strip() else "OK"
        return result
    except subprocess.TimeoutExpired:
        result["stderr"] = "Timeout: 実行に時間がかかりすぎています。"
        return result
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
        status = "ERROR" if "ERROR" in statuses else "NG" if "NG" in statuses else \
            "WARNING" if "WARNING" in statuses else "OK"
        summaries.append({"question": question, "status": status, "results": results})
    return summaries


def run_checker(ml_file):
    student_code = read_file_text(ml_file)
    module_code = extract_btree_module_code(student_code)

    selected = [test for test in TESTS if not test["challenge"]]
    challenge_tests = [test for test in TESTS if test["challenge"]]

    has_btree = re.search(
        r"\bmodule\s+BTree\b(?:(?!\bstruct\b).)*=\s*struct\b",
        _masked_code(student_code),
        re.S,
    ) is not None

    for test in challenge_tests:
        name = test["question"]

        if has_btree:
            implemented = _is_challenge_exported(module_code, name) is True
        else:
            implemented = _defines_challenge_function(student_code, name)

        if implemented:
            selected.append(test)

    return [run_one_test(ml_file, test) for test in selected]