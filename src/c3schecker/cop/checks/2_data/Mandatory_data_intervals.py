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


class Mandatory_data_intervals(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks for mandatory data intervals
    """

    def apply(self):
        self.addinfo = "DataCheck"
        expected_default_intervals = self.consdata.get("default", {}).get(
            "mandatory_intervals", {}
        )
        for var_name, expected_interval in expected_default_intervals.items():
            self._check(expected_interval, var_name)

        for var_name, nc_var in self.cfcollection.variables.items():
            var_constraints = self.consdata.get(var_name, {})
            if not var_constraints:
                continue
            # 2 cases encountered so far:
            # case 1: mandatory_intervals is at the root of the var constraint
            interval_constraints = var_constraints.get("mandatory_intervals")
            if interval_constraints is None:
                # case 2: the root of the var constraint is the cell_method defined
                # on this var
                interval_constraints = var_constraints.get(nc_var.cell_methods, {}).get(
                    "mandatory_intervals"
                )
                # If this is still not it, just mark the check as passed with a warning
                if interval_constraints is None:
                    self.logger.warning(
                        "[%s]- [%s] variable specified in constraints but no "
                        "constraint given",
                        self.getcheckname(self.addinfo),
                        var_name,
                    )
                    continue
            for dependant_var_name, expected_interval in interval_constraints.items():
                self._check(expected_interval, dependant_var_name)

    def _check(self, expected_interval, var_name):
        actual_variable = self.cfcollection.variables.get(var_name)
        if actual_variable is not None:
            for idx in range(1, len(actual_variable)):
                actual_interval = actual_variable[idx] - actual_variable[idx - 1]
                if actual_interval != expected_interval:
                    self.status = 0
                    self.logger.error(
                        "[%s]- [%s] intervals must be %s  - Some other "
                        "intervals has been found - First spurious interval: %s  ",
                        self.getcheckname(self.addinfo),
                        var_name,
                        expected_interval,
                        actual_interval,
                    )
                    break
