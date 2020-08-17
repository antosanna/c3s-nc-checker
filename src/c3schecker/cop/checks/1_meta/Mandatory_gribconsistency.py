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


class Mandatory_gribconsistency(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks for the grib code consistency
    """

    def apply(self):
        self.addinfo = "MetadataCheck"
        # loop sur les datavars si paramid on test
        for var_name, nc_var in list(self.cfcollection.variables.items()):
            if nc_var.mars_paramid:
                for attr in ["units", "standard_name", "long_name"]:
                    nc_var_attr_value = getattr(nc_var, attr)
                    if nc_var_attr_value:
                        attr_value = self.consgrib.get_info(nc_var.mars_paramid, attr)
                        if attr_value is not None:
                            if nc_var_attr_value != attr_value:
                                self.status = 0
                                self.logger.error(
                                    "[%s]-  Non consistency between mars_paramid "
                                    "[%s] [%s=%s] and  variable [%s] [%s=%s]",
                                    self.getcheckname(self.addinfo),
                                    nc_var.mars_paramid,
                                    attr,
                                    attr_value,
                                    var_name,
                                    attr,
                                    nc_var_attr_value,
                                )
