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
import re


class Mandatory_global_attributes_content_pattern(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on global attribute content list
    """

    def apply(self):

        self.addinfo = "MetadataCheck"

        mgavp = self.consmeta.get("mandatory_global_attributes_values_pattern", {})

        for k, v in list(self.cfcollection.global_attributes.items()):
            mgavp_pattern = mgavp.get(k, "")

            if len(mgavp_pattern) > 0 and not re.match(mgavp_pattern, v):
                self.status = 0
                self.logger.error(
                    "[%s]-Global Attribute [%s] value is not allowed - Incorrect string pattern [%s] - It should be [%s]",
                    str(self.getcheckname(self.addinfo)),
                    str(k),
                    str(v),
                    str(mgavp_pattern),
                )
