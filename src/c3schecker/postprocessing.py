import textwrap
from collections import Counter


def print_score_info(check_result):
    lv1_indent = " " * 4
    lv2_indent = lv1_indent * 2
    lv3_indent = lv1_indent * 3
    for filename, outcomes in check_result.items():
        print(f"{filename}:")
        ok, nok, total = compute_score(outcomes)
        print(textwrap.indent(f"Passed: {ok} / {total}", lv1_indent))
        print(textwrap.indent(f"Failed: {nok} / {total}", lv1_indent))
        print(textwrap.indent("Errors:", lv1_indent))
        failed_outcomes = {cn: oc for cn, oc in outcomes.items() if oc["status"] == 0}
        for check_name, outcome in failed_outcomes.items():
            print(textwrap.indent(f"{check_name}:", lv2_indent))
            for err_msg in outcome["errors"]:
                print(textwrap.indent(f"{err_msg}", lv3_indent))


def compute_score(outcome):
    counter = Counter(check_outcome["status"] for check_outcome in outcome.values())
    return counter[1], counter[0], len(outcome)
