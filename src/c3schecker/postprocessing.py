import textwrap
from collections import Counter
import logging


def print_score_info(check_result, verbose):
    lv1_indent = " " * 4
    lv2_indent = lv1_indent * 2
    lv3_indent = lv1_indent * 3
    for filename, outcomes in check_result.items():
        ok, nok, total = compute_score(outcomes)
        logging.info(
            "====================================================================="
        )
        logging.info(f"File: {filename}:")
        logging.info(f"Results: ")
        logging.info(textwrap.indent(f"Total  tests: {total}", lv1_indent))
        logging.info(textwrap.indent(f"Passed tests: {ok}", lv1_indent))
        logging.error(textwrap.indent(f"Failed tests: {nok}", lv1_indent))
        if not verbose:
            errors_outcomes = {
                cn: oc for cn, oc in outcomes.items() if oc.get("errors", {})
            }
            logging.error(textwrap.indent(f"Errors results:", lv1_indent))
            for check_name, outcome in errors_outcomes.items():
                logging.error(textwrap.indent(f"Check name: {check_name}:", lv2_indent))
                for err_msg in outcome["errors"]:
                    logging.error(textwrap.indent(f"{err_msg}", lv3_indent))

            logging.warning(textwrap.indent(f"Warnings results:", lv1_indent))
            warnings_outcomes = {
                cn: oc for cn, oc in outcomes.items() if oc.get("warnings", {})
            }
            for check_name, outcome in warnings_outcomes.items():
                logging.warning(
                    textwrap.indent(f"Check name: {check_name}:", lv2_indent)
                )
                for wrn_msg in outcome["warnings"]:
                    logging.warning(textwrap.indent(f"{wrn_msg}", lv3_indent))


def compute_score(outcome):
    counter = Counter(check_outcome["status"] for check_outcome in outcome.values())
    return counter[1], counter[0], len(outcome)
