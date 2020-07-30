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


class Mandatory_attributes_content(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on attribute contents
    """

    def apply(self):
        self.addinfo = "MetadataCheck"
        expected = self.consmeta["mandatory_attributes_values"]
        for var_name, var in self.cfcollection.variables.items():
            cf_attrs = var.ncattrs()
            for attr_name in cf_attrs:
                possible_values = []
                for val in expected.get(attr_name, []):
                    try:
                        possible_values.append(float(val))
                    except ValueError:
                        possible_values.append(val)
                    actual_value = var.getncattr(attr_name)
                    if not (actual_value in possible_values):
                        self.status = 0
                        self.logger.error(
                            "[%s]-Attribute [%s] [%s] value is not allowed - "
                            "Variable [%s] - Should be one of %s ",
                            str(self.getcheckname(self.addinfo)),
                            str(attr_name),
                            str(actual_value),
                            str(var_name),
                            str(possible_values),
                        )
