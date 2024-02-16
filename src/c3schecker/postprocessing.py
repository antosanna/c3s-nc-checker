import textwrap
from collections import Counter
import logging


def print_score_info(check_result):
    lv1_indent = " " * 4
    lv2_indent = lv1_indent * 2
    lv3_indent = lv1_indent * 3
    for filename, outcomes in check_result.items():
        ok, nok, total = compute_score(outcomes)
        #print("=====================================================================")
        logging.info("=====================================================================")
        logging.info(f"File: {filename}:")
        logging.info(f"Results: ")
        #print(textwrap.indent(f"Total  tests: {total}", lv1_indent))
        logging.info(textwrap.indent(f"Total  tests: {total}", lv1_indent))
        ###print(textwrap.indent(f"Passed tests: {ok} / {total}", lv1_indent))
        ###print(textwrap.indent(f"Failed tests: {nok} / {total}", lv1_indent))
        #print(textwrap.indent(f"Passed tests: {ok}", lv1_indent))
        #print(textwrap.indent(f"Failed tests: {nok}", lv1_indent))
        logging.info(textwrap.indent(f"Passed tests: {ok}", lv1_indent))
        logging.error(textwrap.indent(f"Failed tests: {nok}", lv1_indent))
        #print("=====================================================================")
        #print(textwrap.indent("Errors:", lv1_indent))
        failed_outcomes = {cn: oc for cn, oc in outcomes.items() if oc["status"] == 0}
        #print(textwrap.indent(f"Failed test(s) results:", lv1_indent))
        logging.error(textwrap.indent(f"Failed test(s) results:", lv1_indent))
        for check_name, outcome in failed_outcomes.items():
            #print(textwrap.indent(f"{check_name}:", lv2_indent))
            logging.error(textwrap.indent(f"Check name: {check_name}:", lv2_indent))
            for err_msg in outcome["errors"]:
                #print(textwrap.indent(f"{err_msg}", lv3_indent))
                logging.error(textwrap.indent(f"{err_msg}", lv3_indent))


def compute_score(outcome):
    #for check_outcome in outcome.values():
    #    print(check_outcome["status"])
    counter = Counter(check_outcome["status"] for check_outcome in outcome.values())
    return counter[1], counter[0], len(outcome)
