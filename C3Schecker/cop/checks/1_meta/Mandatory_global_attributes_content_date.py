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
import datetime

class Mandatory_global_attributes_content_date(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on global attribute content list
    """

    def apply(self):

        self.addinfo = "MetadataCheck"

        mgavd = self.consmeta.get("mandatory_global_attributes_values_date", {})

        for k, v in list(self.cfcollection.global_attributes.items()):
            mgavd_dateformat =  mgavd.get(k, "")

            if len(mgavd_dateformat) > 0:
                try:
                    datetime.datetime.strptime(v, mgavd_dateformat)
                except ValueError:
                    self.status = 0
                    self.logger.error("[%s]-Global Attribute [%s] value is not allowed - Incorrect data format [%s] - It should be [%s]", str(self.getcheckname(self.addinfo)), str(k), str(v), str(mgavd_dateformat) )
