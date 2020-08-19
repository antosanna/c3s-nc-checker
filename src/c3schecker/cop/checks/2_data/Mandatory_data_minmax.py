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

from ..Basiccpcheck import Basiccheck


class Mandatory_data_minmax(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks for mandatory data minimum and maximum (can be used for global fields)
    """

    def apply(self):
        self.addinfo = "DataCheck"
        for var_name, nc_var in self.cfcollection.variables.items():
            # First check if there is a constraint at the root of the constraint dict
            var_min_max_constraints = self.consdata.get(var_name, {}).get(
                "mandatory_min_max"
            )
            if var_min_max_constraints is None:
                # If not, check if there is one in the default key of the
                # constraint dict
                var_min_max_constraints = (
                    self.consdata.get("default", {})
                    .get("mandatory_min_max", {})
                    .get(var_name)
                )
            self._check(var_name, nc_var, var_min_max_constraints)

    def _check(self, var_name, nc_var, var_min_max_constraints):
        if var_min_max_constraints:
            if nc_var is not None:
                nc_var_values = nc_var[:].data
                expected_min = min(var_min_max_constraints)
                expected_max = max(var_min_max_constraints)
                actual_min = nc_var_values.min()
                actual_max = nc_var_values.max()
                self._assert(var_name, actual_min, expected_min, "minimum")
                self._assert(var_name, actual_max, expected_max, "maximum")

    def _assert(self, var_name, actual, expected, category):
        try:
            assert actual == expected
        except AssertionError:
            self.status = 0
            self.logger.error(
                "[%s]- [%s] %s value must be %s - Currently %s",
                self.getcheckname(self.addinfo),
                var_name,
                category,
                expected,
                actual,
            )
