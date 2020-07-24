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


class Mandatory_global_attributes_content(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on global attribute content
    """

    def apply(self):

        self.addinfo = "MetadataCheck"

        mgac = self.consmeta.get("mandatory_global_attributes_values", {})

        for k, v in list(self.cfcollection.global_attributes.items()):
            mgac_possiblevalues = [str(a) for a in mgac.get(k, [])]

            if v not in mgac_possiblevalues and len(mgac_possiblevalues) > 0:
                self.status = 0
                self.logger.error("[%s]-Global Attribute [%s] value is not allowed - Should be one of %s - currently [%s]", str(self.getcheckname(self.addinfo)), str(k), str(mgac_possiblevalues), str(v))
