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

import numpy as np
from numpy.ma import MaskedArray

from ..Basiccpcheck import Basiccheck


class Mandatory_data_values(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks for mandatory data in a list of values
    """

    def apply(self):
        self.addinfo = "DataCheck"
        for var_name, nc_var in self.cfcollection.variables.items():
            # First check if there is a constraint at the root of the constraint dict
            var_values_constraints = self.consdata.get(var_name, {}).get(
                "mandatory_values"
            )
            if var_values_constraints is None:
                # If not, check if there is one in the default key of the
                # constraint dict
                var_values_constraints = (
                    self.consdata.get("default", {})
                    .get("mandatory_values", {})
                    .get(var_name)
                )
            self._check(var_name, nc_var, var_values_constraints)

    def _check(self, var_name, nc_var, data_values_constraints):
        if data_values_constraints:
            if nc_var is not None:
                data = nc_var[:]
                if isinstance(data, MaskedArray):
                    data = data.compressed()
                invalid = np.asarray(data - data_values_constraints != 0).nonzero()[0]
                if invalid.size > 0:
                    self.status = 0
                    self.logger.error(
                        "[%s]- [%s] values must exactly equal %s - currently: %s",
                        self.getcheckname(self.addinfo),
                        var_name,
                        data_values_constraints,
                        data,
                    )
