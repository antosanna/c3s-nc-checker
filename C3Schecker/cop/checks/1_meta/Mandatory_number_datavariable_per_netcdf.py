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

from C3Schecker.cop.checks.Basiccpcheck import Basiccheck


class Mandatory_number_datavariable_per_netcdf(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on the number of data variable per netCDF file
    """

    def apply(self):

        self.addinfo = "MetadataCheck"

        ndpn = self.consmeta.get("mandatory_number_datavariable_per_netcdf", None)
        datavars = list(self.cfcollection.data_variables.keys())
        if len(datavars) != ndpn and ndpn:
            self.status = 0
            self.logger.error("[%s]-Only [%s] Data Variable should be contained in a file - currently [%s] identified: %s ", str(self.getcheckname(self.addinfo)), str(ndpn), str(len(datavars)), str(datavars))
