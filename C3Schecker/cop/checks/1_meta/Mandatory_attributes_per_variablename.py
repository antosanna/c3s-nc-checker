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

from Basiccpcheck import Basiccheck


class Mandatory_attributes_per_variablename(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on mandatory attributes according to short names
    """

    def apply(self):

        mapv = self.consmeta.get("mandatory_attributes_per_variablename", {})
        for k, v in self.cfcollection:

            mandatoryattributes = mapv.get(k, [])
            cfattrs = v.attributesnames

            if len(mandatoryattributes) > 0:
                for attr in mandatoryattributes:
                    if attr not in cfattrs:
                        self.status = 0
                        self.logger.error("[%s]-Attribute [%s] is mandatory - Variable [%s] ", str(self.ref), str(attr), str(k))
