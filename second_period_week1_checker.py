# -*- coding: utf-8 -*-

"""Second-period Week1 checker scaffold.

Start as a clone/proxy of run_checker and customize TESTS/logic for:
count_ones / power_val / power_steps / collatz_steps / collatz_path.
"""

import run_checker

TESTS = run_checker.TESTS


def run_one_test(ml_file, test):
    return run_checker.run_one_test(ml_file, test)


def summarize_by_question(file_results):
    return run_checker.summarize_by_question(file_results)
