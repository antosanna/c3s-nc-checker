#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: C. BERGERON -
#
# Note: None
#
#
# (C) Copyright 1996-2016 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import os
import re
import xml.etree.ElementTree as ElementTree

import numpy as np


def cf_reference():
    return "[CFREF]  NetCDF Climate and Forecast (CF) Metadata conventions, Version 1.6,  5 December, 2011"


def cf_allowed_datatypes():

    cf_allowed_datatypes = [
        np.dtype("S1"),
        np.dtype("c"),
        np.dtype("b"),
        np.dtype("i4"),
        np.int32,
        np.int64,
        np.float32,
        np.double,
    ]

    return cf_allowed_datatypes


def cf_Xaxis_standard_names():
    return ["longitude", "projection_x_coordinate", "grid_longitude"]


def cf_Yaxis_standard_names():
    return ["latitude", "projection_y_coordinate", "grid_latitude"]


def cf_Zaxis_standard_names():
    return [
        "atmosphere_ln_pressure_coordinate",
        "atmosphere_sigma_coordinate",
        "atmosphere_hybrid_sigma_pressure_coordinate",
        "atmosphere_hybrid_height_coordinate",
        "atmosphere_sleve_coordinate",
        "ocean_sigma_coordinate",
        "ocean_s_coordinate",
        "ocean_s_coordinate_g1",
        "ocean_s_coordinate_g2",
        "ocean_sigma_z_coordinate",
        "ocean_double_sigma_coordinate",
    ]


def cf_Zaxis_units():
    return ["level", "layer" "sigma_level"]


def cf_Taxis_standard_names():
    return ["time", "forecast_reference_time"]


def cf_recommended_globals():
    return ["title", "institution", "source", "history", "references", "comment"]


def cf_deprecated_units():
    return ["level", "layer", "sigma_level"]


def cf_latitude_units():
    # Index 0 is the recommended one
    return [
        "degrees_north",
        "degree_north",
        "degree_N",
        "degrees_N",
        "degreeN",
        "degreesN",
    ]


def cf_longitude_units():
    # Index 0 is the recommended one
    return [
        "degrees_east",
        "degree_east",
        "degree_E",
        "degrees_E",
        "degreeE",
        "degreesE",
    ]


def cf_standard_names():

    entries = {}
    tree = ElementTree.parse(
        os.path.join(os.path.dirname(__file__), "resources/cf-standard-name-table.xml")
    )

    i = 0
    for element in tree.iter("entry"):
        entries[element.attrib["id"]] = element.find("canonical_units").text

    return entries


def cf_standard_names_modifiers():
    """Contains modified unit. None means no unit modification (or at least equivalent)"""

    return {
        "detection_minimum": None,
        "number_of_observations": "1",
        "standard_error": None,
        "status_flag": None,
    }


def cf_dimensionless_vertical_coordinates():
    return {
        "atmosphere_ln_pressure_coordinate",
        "atmosphere_sigma_coordinate",
        "atmosphere_hybrid_sigma_pressure_coordinate",
        "atmosphere_hybrid_height_coordinate",
        "atmosphere_sleve_coordinate",
        "ocean_sigma_coordinate",
        "ocean_s_coordinate",
        "ocean_sigma_z_coordinate",
        "ocean_double_sigma_coordinate",
    }


def cf_calendars():

    return [
        "gregorian",
        "standard",
        "proleptic_gregorian",
        "noleap",
        "365_day",
        "all_leap",
        "366_day",
        "360_day",
        "julian",
        "none",
    ]


def cf_positive_values():
    return ["up", "down"]


def cf_formulaterm_measure_pattern():
    return re.compile(
        r"""
                           \s*
                           (?P<lhs>[\w_]+)
                           \s*:\s*
                           (?P<rhs>[\w_]+)
                           \s*
                        """,
        re.VERBOSE,
    )


def cf_excluded_attributes():
    return set(["_FillValue", "missing_value", "scale_factor", "add_offset"])


def cf_cell_methods():
    cf_methods = [
        "point",
        "sum",
        "maximum",
        "Maximum",
        "median",
        "Median",
        "mid_range",
        "minimum",
        "Minimum",
        "mean",
        "mode",
        "standard_deviation",
        "variance",
    ]
    return cf_methods
