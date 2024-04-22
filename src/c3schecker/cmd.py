#!/usr/bin/env python
#
# c3schecker checks NetCDF compliancy for C3S data
#
# AUTHOR: ECMWF - Adrien OYONO OWONO, Charalampos KARVELIS
#
# (C) Copyright 2020-2024 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#
import datetime
import importlib
import json
import logging
import sys
from pathlib import Path

import click
from netCDF4 import Dataset
from pkg_resources import resource_filename

from c3schecker.checks import ChecksRegistry
from c3schecker.postprocessing import print_score_info, compute_score

# First import all existing conventions in order to register all the available checks
# We do this with importlib so that we don't have unused imports at the top
importlib.import_module("c3schecker.checks.c3s_tests")
importlib.import_module("c3schecker.checks.cf_tests")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)


def list_tests(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("List of all the available tests:")
    for name, _ in ChecksRegistry().__contains__().items():
        click.echo(f"     - {name}")
    ctx.exit()


@click.command("c3s-checker")
@click.option(
    "-t",
    "--tests",
    "tests",
    multiple=True,
    help="Specific test (s) to be run",
)
@click.option(
    "-f",
    "--tests-family",
    required=False,
    default="all",
    show_default=True,
    type=click.Choice(["c3s", "cf", "cerise", "all"]),
    help="Specific group of tests to be run",
)
@click.option(
    "--constraints",
    required=False,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, allow_dash=True),
    help=(
        "JSON file representing the constraints for the convention that the NetCDF "
        "file(s) must follow. If this is not given, The -C/--convention option is used "
        "to load a default constraint file embedded with the package (see the option's "
        "docs). Otherwise, the -C/--convention is ignored."
    ),
)
@click.option(
    "--exceptions",
    required=False,
    help=(
        "JSON file representing what kind of deviation from the constraints are "
        "authorized. If a test fails but that failure is specified in this file, the "
        "overall test result isn't affected."
    ),
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, allow_dash=True),
)
@click.option(
    "--convention",
    "-C",
    required=False,
    default="C3S-0.3",
    show_default=True,
    type=click.Choice(["C3S-0.1", "C3S-0.2", "C3S-0.3"]),
    help=(
        "The NetCDF convention to use for the test suite. This is used to load a "
        "default constraint file corresponding to the convention, and is ignored if "
        "the --constraints option is given."
    ),
    callback=lambda ctx, param, value: set(value),
)
@click.option(
    "--json", "js", help="Print output in json format", is_flag=True, flag_value=True
)
@click.option(
    "--score-threshold",
    help=(
        "The minimum score a file must have to be considered as passing all "
        "the checks (expressed as a percentage - i.e between 0 and 100). "
        "For operational run the score should be 100"
    ),
    type=click.IntRange(min=0, max=100),
    default=100,
    show_default=True,
)
@click.option(
    "--min-passing-files",
    help=(
        "The minimum number of files that must pass to consider the command as "
        "passing (expressed as a percentage - i.e between 0 and 100) "
        "For operational runs all the files should have pass all the tests."
    ),
    type=click.IntRange(min=0, max=100),
    default=100,
    show_default=True,
)
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode")
@click.option(
    "-p",
    "--operational",
    is_flag=True,
    help="Run in operational mode, where any failed test makes the overall test fail",
)
@click.option(
    "-l",
    "--list-tests",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=list_tests,
    help=(
        "List the available tests that can be executed. Run this first if you want to "
        "select only a few tests to run"
    ),
)
@click.argument(
    "inputs", nargs=-1, callback=lambda ctx, param, value: [Path(v) for v in value]
)
def main(
    inputs,
    tests_family,
    convention,
    constraints,
    exceptions,
    tests,
    js,
    verbose,
    operational,
    score_threshold,
    min_passing_files,
):
    """Check the input NetCDF files against a specified convention or set of
    constraints"""

    logging.info("")
    logging.info(
        "====================================================================="
    )
    logging.info("")
    logging.info("        ECMWF NetCDF Checker")
    logging.info(
        f"        Report generated at "
        f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    logging.info("")
    logging.info(
        "====================================================================="
    )

    checks_all = {
        name: func
        for name, func in ChecksRegistry().items()
        if not tests or tests and name in set(tests)
    }

    if tests_family == "c3s":
        tests_list = [
            "c3s_filename_convention",
            "c3s_filename_reconstruction",
            "c3s_metadata_convention",
            "c3s_netcdf_format",
            "c3s_scientific_variables_per_file",
            "c3s_dimensions",
            "c3s_dimensions_per_variable",
            "c3s_variables",
            "c3s_coordinates_attributes",
            "c3s_calendar",
            "c3s_exact_attributes_values",
            "c3s_global_attributes",
            "c3s_global_attributes_values",
            "c3s_global_date_attributes_format",
            "c3s_variables_exact_dimensions",
            "c3s_data_intervals",
            "c3s_data_min_max",
            "c3s_data_ranges",
            "c3s_data_values",
            "c3s_variable_units",
            "c3s_time_bnds_consistency",
            "c3s_time_values",
            "c3s_time_consistency",
            "c3s_missing_values_consistency",
            "c3s_realization_format",
        ]
    elif tests_family == "cf":
        tests_list = [
            "cf_filename_extension",
            "cf_convention",
            "cf_data_types",
            "cf_dimensions_order",
            "cf_dimensions_unicity",
            "cf_global_attributes",
            "cf_missing_data",
            "cf_attributes_values_type",
            "cf_naming_convention",
            "cf_naming_unicity",
            "cf_ancillary_data",
            "cf_standard_names",
            "cf_units",
            "cf_flags",
            "cf_coordinates_variables",
            "cf_dimensionless_vertical_coordinates",
            "cf_latitude",
            "cf_longitude",
            "cf_time",
            "cf_coordinates",
            "cf_cell_methods",
        ]
    elif tests_family == "cerise":
        tests_list = [
            "c3s_filename_convention",
            "c3s_filename_reconstruction",
            "c3s_coordinates_attributes",
        ]
    else:
        tests_list = checks_all

    if tests_family:
        checks = {
            name: func for name, func in checks_all.items() if name in set(tests_list)
        }

    if constraints:
        logging.info(f"Using the provided constraint file: {constraints}")
    else:
        logging.info(f"File(s) will be checked against the conventions: {convention}")
        if "C3S-0.1" == convention:
            constraints = resource_filename(
                "c3schecker", "resources/c3s01_seasonal_constraints.json"
            )
            logging.info(
                f"The default C3S-0.1 constrains will "
                f"be used for the checks [{constraints}]"
            )
        elif "C3S-0.2" == convention:
            constraints = resource_filename(
                "c3schecker", "resources/c3s01_seasonal_constraints.json"
            )
            logging.info(
                f"The default C3S-0.1 (same as C3S-0.1) constrains will "
                f"be used for the checks [{constraints}]"
            )
        elif "C3S-0.3" == convention:
            constraints = resource_filename(
                "c3schecker", "resources/c3s03_seasonal_constraints.json"
            )
            logging.info(
                f"The default C3S-0.3 constrains will "
                f"be used for the checks [{constraints}]"
            )

    with open(constraints) as fd:
        spec = json.load(fd)

    # Exceptions
    if exceptions:
        with open(exceptions) as file:
            c3s_excep = json.load(file)
        logging.info(f"Users exceptions: {exceptions}")
    else:
        c3s_excep = {}

    logging.info(
        "====================================================================="
    )
    logging.info(f"Start running the checks")
    logging.info(
        "====================================================================="
    )
    result = run_checks(inputs, checks, spec, c3s_excep, verbose, operational)
    logging.info(
        "====================================================================="
    )
    logging.info(f"Print scores")
    logging.info(
        "====================================================================="
    )
    if js:
        print(json.dumps(result))
    else:
        print_score_info(result, verbose)
    # Exit with anomalous code if there is even 1 failed check
    nb_passing_files = 0
    logging.info(
        "====================================================================="
    )
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

            file_outcome = outcomes.setdefault(input_file.name, {})
            for check_name, check in checks.items():
                if verbose:
                    logging.info("--------------------------------------------")
                    logging.info(f"Running check : {check_name}")
                outcome = check(dataset, spec, c3s_excep, verbose, operational)
                file_outcome[check_name] = outcome
                if verbose:
                    if outcome["status"] == 1:
                        logging.info(f"Check#{i} was OK.")
                    else:
                        logging.error(f"Check#{i} was KO. ")
                i += 1
        except OSError:
            logging.error(f"Not a NetCDF file, skipping ... ")

    return outcomes


if __name__ == "__main__":
    sys.exit(main())
