#!/usr/bin/env python
#
# c3schecker checks NetCDF compliancy for C3S data
#
# AUTHOR: ECMWF - C. BERGERON, A. OYONO
#
# (C) Copyright 1996-2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#
import importlib
import json
import sys
from pathlib import Path
import datetime
import logging

import click
from netCDF4 import Dataset
from pkg_resources import resource_filename

from c3schecker.checks import ChecksRegistry


# First import all existing conventions in order to register all the available checks
# We do this with importlib so that we don't have unused imports at the top
from c3schecker.postprocessing import print_score_info, compute_score

importlib.import_module("c3schecker.checks.c3s01")
importlib.import_module("c3schecker.checks.cf16")

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s | %(levelname)-8s | %(message)s",
                    datefmt='%d-%m-%Y %H:%M:%S')

@click.command("c3schecker")
@click.option(
    "-c",
    "checks",
    multiple=True,
    help="Specific constraints to be checked (only the specified ones will be done)",
)
@click.option(
    "--constraints",
    required=False,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, allow_dash=True),
)
@click.option("--c3sexceptions", required=False,
    help="Specific C3S exceptions to be used",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, allow_dash=True),
)
@click.option(
    "--convention",
    "-C",
    "conventions",
    required=True,
    multiple=True,
    type=click.STRING,
    help="The NetCDF convention followed by the constraints file",
    callback=lambda ctx, param, value: set(value),
)
@click.option(
    "--json", "js", help="Print output in json format", is_flag=True, flag_value=True
)
@click.option(
    "--score-threshold",
    help=(
        "The minimum score a file must have to be considered as passing all "
        "the checks (expressed as a percentage - i.e between 0 and 100)"
    ),
    type=click.IntRange(min=0, max=100),
    default=100,
    show_default=True,
)
@click.option(
    "--min-passing-files",
    help=(
        "The minimum number of files that must pass to consider the command as "
        "passing (expressed as a percentage - i.e between 0 and 100)"
    ),
    type=click.IntRange(min=0, max=100),
    default=100,
    show_default=True,
)
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-p', '--operational', is_flag=True, help='Operational check')
@click.argument(
    "inputs", nargs=-1, callback=lambda ctx, param, value: [Path(v) for v in value]
)
def main(
    inputs, conventions, constraints, c3sexceptions, checks, js, verbose, operational, score_threshold, min_passing_files
):
    """Check the input NetCDF files against the specified constraints file"""
    
    # print('')
    # print("=====================================================================")
    # print('')
    # print("        ECMWF C3S Checker")
    # print(f"        Report generated at "
    #       f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # print(f"        Convention(s) {' '.join(conventions)}")
    # print("        !!! Testing version !!!")
    # print('')
    # print("=====================================================================")

    logging.info('')
    logging.info("=====================================================================")
    logging.info('')
    logging.info("        ECMWF C3S Checker")
    logging.info(f"        Report generated at "
          f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"        Convention(s) {' '.join(conventions)}")
    logging.info("        !!! Testing version !!!")
    logging.info('')
    logging.info("=====================================================================")

    logging.info(f"Conventions: {conventions}")
    
    if not constraints:
        if "C3S-0.1" in conventions:
            constraints = resource_filename(
                "c3schecker", "resources/c3s01_seasonal_constraints.json"
            )
            logging.info(
            f"The default C3S-0.1 constrains will "
            f"be used for the checks [{constraints}]"
            )
        if "C3S-0.2" in conventions:
            constraints = resource_filename(
                "c3schecker", "resources/c3s02_seasonal_constraints.json"
            )
            logging.info(
            f"The default C3S-0.1 constrains will "
            f"be used for the checks [{constraints}]"
            )    
    
    checks = {
        name: func
        for convention in conventions
        for name, func in ChecksRegistry()[convention].items()
        if not checks or checks and name in set(checks)
    }

    #logging.info(f"checks {checks}")
    

    # Constraints
    if constraints:
        with open(constraints) as cf:
            spec = json.load(cf)
    else:
        spec = {}
    
    # Exceptions
    if c3sexceptions:
        with open(c3sexceptions) as file:
            c3s_excep = json.load(file)
        logging.info(f"Users C3S exceptions: {c3sexceptions}")
    else:
        c3s_excep = {}
    
    # print("=====================================================================")
    logging.info("=====================================================================")
    logging.info(f"Start running the checks")   
    # print("=====================================================================")
    logging.info("=====================================================================")
    result = run_checks(inputs, checks, spec, c3s_excep, verbose, operational)
    # print("=====================================================================")
    logging.info("=====================================================================")
    logging.info(f"Print scores")
    # print("=====================================================================")
    logging.info("=====================================================================")
    if js:
        print(json.dumps(result))
    else:
        print_score_info(result, verbose)
    # Exit with anomalous code if there is even 1 failed check
    nb_passing_files = 0
    #print("=====================================================================")
    logging.info("=====================================================================")
    logging.info("Summary of the passed/failed file(s)")
    for filename, outcome in result.items():
        score, _, total = compute_score(outcome)
        if score * 100 / total >= score_threshold:
            logging.info(f"{str(filename):<90}: Passed")
            nb_passing_files += 1
        else:
            logging.error(f"{str(filename):<90}: Failed")
    if nb_passing_files * 100 / len(inputs) < min_passing_files:
        sys.exit(1)
    sys.exit(0)


def run_checks(input_files, checks, spec, c3s_excep, verbose, operational):
    outcomes = {}
    for input_file in input_files:
        i = 1 
        logging.info("--------------------------------------------")
        logging.info(f"Checking file: [{input_file}]")
        try:
            dataset = Dataset(input_file)
        except OSError:
            logging.error(f"Not an NetCDF file, continue ... ")
        file_outcome = outcomes.setdefault(input_file.name, {})
        for check_name, check in checks.items():
            if verbose:
                logging.info("--------------------------------------------")
                logging.info(f"Running check : {check_name}")
            outcome = check(dataset, spec, c3s_excep, verbose, operational)
            file_outcome[check_name] = outcome
            if verbose:
                if outcome['status'] == 1:
                    logging.info(f"Check#{i} was successful.")
                else:
                    logging.error(f"Check#{i} was failed. ")
            i += 1

    return outcomes


if __name__ == "__main__":
    sys.exit(main())
