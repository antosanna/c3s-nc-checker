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


class Mandatory_global_attributes(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks for mandatory global attributes
    """

    def apply(self):

        mga = self.consmeta.get("mandatory_global_attributes", {})
        for i in mga:
            if i not in self.cfcollection.global_attributes.keys():
                self.status = 0
                self.logger.error("[%s]-Global Attribute [%s] is missing", str(self.ref), str(i))
