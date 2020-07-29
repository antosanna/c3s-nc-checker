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


class Mandatory_attributes_per_standardname(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on mandatory attributes according to short names
    """

    def apply(self):
        self.addinfo = "MetadataCheck"
        expected = self.consmeta["mandatory_attributes_per_standardname"]
        for var_name, nc_var in self.cfcollection.variables.items():
            nc_var_attrs = nc_var.ncattrs()
            std_name = nc_var.standard_name
            expected_nc_var_mandatory_attrs = expected.get(std_name, [])
            if len(expected_nc_var_mandatory_attrs) > 0:
                for attr in expected_nc_var_mandatory_attrs:
                    if attr not in nc_var_attrs:
                        self.status = 0
                        self.logger.error(
                            "[%s]-Attribute [%s] is mandatory - Variable [%s] ",
                            str(self.getcheckname(self.addinfo)),
                            str(attr),
                            str(var_name),
                        )
