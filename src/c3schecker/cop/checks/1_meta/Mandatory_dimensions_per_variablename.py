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


class Mandatory_dimensions_per_variablename(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on dimensions . Test is mandatory_dimensions exist
    """

    def apply(self):
        self.addinfo = "MetadataCheck"
        expected = self.consmeta["mandatory_attributes_values_per_variablename"]
        for var_name, nc_var in self.cfcollection.variables.items():
            expected_dimensions = expected.get(var_name, {}).get("dimensions")
            if expected_dimensions is not None:
                actual_dimensions = nc_var.dimensions
                for mandatory_dim in expected_dimensions:
                    if mandatory_dim not in actual_dimensions:
                        self.status = 0
                        self.logger.error(
                            "[%s]-NetCDF Dimensions must contain %s  used for "
                            "variable %s - currently %s ",
                            str(self.getcheckname(self.addinfo)),
                            mandatory_dim,
                            var_name,
                            actual_dimensions,
                        )
