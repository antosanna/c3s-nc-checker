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

import click
from netCDF4 import Dataset
from pkg_resources import resource_filename

from c3schecker.checks import ChecksRegistry


# First import all existing conventions in order to register all the available checks
# We do this with importlib so that we don't have unused imports at the top
from c3schecker.postprocessing import print_score_info

importlib.import_module("c3schecker.checks.c3s01")
importlib.import_module("c3schecker.checks.cf16")


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
@click.argument(
    "inputs", nargs=-1, callback=lambda ctx, param, value: [Path(v) for v in value]
)
def main(inputs, conventions, constraints, checks, js):
    """Check the input NetCDF files against the specified constraints file"""
    if not constraints:
        if "C3S-0.1" in conventions:
            constraints = resource_filename(
                "c3schecker", "resources/c3s01_seasonal_constraints.json"
            )
    checks = {
        name: func
        for convention in conventions
        for name, func in ChecksRegistry()[convention].items()
        if not checks or checks and name in set(checks)
    }
    if constraints:
        with open(constraints) as cf:
            spec = json.load(cf)
    else:
        spec = {}
    result = run_checks(inputs, checks, spec)
    print_score_info(result)
    if js:
        print(json.dumps(result))
    # Exit with anomalous code if there is even 1 failed check
    for outcome in result.values():
        for check_outcome in outcome.values():
            if check_outcome["status"] == 0:
                sys.exit(1)
    sys.exit(0)


def run_checks(input_files, checks, spec):
    outcomes = {}
    for input_file in input_files:
        dataset = Dataset(input_file)
        file_outcome = outcomes.setdefault(input_file.name, {})
        for check_name, check in checks.items():
            # print(f"Running check: {check}")
            outcome = check(dataset, spec)
            file_outcome[check_name] = outcome
    return outcomes


if __name__ == "__main__":
    sys.exit(main())
