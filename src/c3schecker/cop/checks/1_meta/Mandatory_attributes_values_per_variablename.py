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

import re

from ..Basiccpcheck import Basiccheck


class Mandatory_attributes_values_per_variablename(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on mandatory attributes according to short names
    """

    def apply(self):
        self.addinfo = "MetadataCheck"
        expected = self.consmeta["mandatory_attributes_values_per_variablename"]
        # Some of the attribute values should be checked against a regular expression
        regex_special = ["cell_methods"]
        for var_name, nc_var in self.cfcollection.variables.items():
            expected_nc_var_mandatory_attrs = {
                k: v for k, v in expected.get(var_name, {}).items() if k != "dimensions"
            }
            actual_nc_var_attrs = nc_var.ncattrs()
            if len(expected_nc_var_mandatory_attrs) > 0:
                for attr in expected_nc_var_mandatory_attrs:
                    if attr in actual_nc_var_attrs:
                        expected_attr_value = expected_nc_var_mandatory_attrs[attr]
                        actual_attr_value = nc_var.getncattr(attr)
                        if attr in regex_special:
                            if not re.match(expected_attr_value, actual_attr_value):
                                self.status = 0
                                self.logger.error(
                                    "[%s]-Wrong [%s] value - Variable [%s]; [%s] does "
                                    "not match [%s]",
                                    str(self.getcheckname(self.addinfo)),
                                    str(attr),
                                    str(var_name),
                                    str(expected_attr_value),
                                    str(actual_attr_value),
                                )
                        else:
                            if actual_attr_value != expected_attr_value:
                                self.status = 0
                                self.logger.error(
                                    "[%s]-Wrong [%s] value - Variable [%s]; [%s] "
                                    "expected but [%s] found ",
                                    str(self.getcheckname(self.addinfo)),
                                    str(attr),
                                    str(var_name),
                                    str(expected_attr_value),
                                    str(actual_attr_value),
                                )
                    else:
                        self.status = 0
                        self.logger.error(
                            "[%s]-[%s] is missing - Variable [%s];",
                            str(self.getcheckname(self.addinfo)),
                            str(attr),
                            str(var_name),
                        )
