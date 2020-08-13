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


class Mandatory_attributes_per_variablename(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on mandatory attributes according to short names
    """

    def apply(self):
        self.addinfo = "MetadataCheck"
        expected = self.consmeta["mandatory_attributes_per_variablename"]
        for var_name, nc_var in self.cfcollection.variables.items():
            expected_attrs = expected.get(var_name, [])
            actual_attrs = nc_var.ncattrs()
            for expected_attr in expected_attrs:
                if expected_attr not in actual_attrs:
                    self.status = 0
                    self.logger.error(
                        "[%s]-Attribute [%s] is mandatory - Variable [%s] ",
                        str(self.getcheckname(self.addinfo)),
                        expected_attr,
                        var_name,
                    )
