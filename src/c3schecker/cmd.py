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

from c3schecker.checks import ChecksRegistry


# First import c3s01 in order to register all the available checks
# We do this with importlib so that we don't have unused imports at the top
importlib.import_module("c3schecker.checks.c3s01")
DEFAULT_CONVENTION = "C3S-0.1"


@click.command("c3schecker")
@click.option(
    "-c",
    "checks",
    multiple=True,
    help="Specific constraints to be checked (only the specified ones will be done)",
    default=set(ChecksRegistry()[DEFAULT_CONVENTION].keys()),
    show_default=True,
)
@click.option(
    "-s",
    "--skip",
    multiple=True,
    help="Specific constraints to skip (specify as in -c)",
    default=set(),
)
@click.option(
    "--constraints",
    required=True,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, allow_dash=True),
)
@click.option(
    "--convention",
    required=True,
    type=click.STRING,
    default=DEFAULT_CONVENTION,
    help="The NetCDF convention followed by the constraints file",
    show_default=True,
)
@click.argument(
    "inputs", nargs=-1, callback=lambda ctx, param, value: [Path(v) for v in value]
)
def main(inputs, convention, constraints, skip, checks):
    """Check the input NetCDF files against the specified constraints file"""
    checks = {
        name: func
        for name, func in ChecksRegistry()[convention].items()
        if name in set(checks) - set(skip)
    }
    with open(constraints) as cf:
        spec = json.load(cf)
    print(json.dumps(run_checks(inputs, checks, spec)))


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
