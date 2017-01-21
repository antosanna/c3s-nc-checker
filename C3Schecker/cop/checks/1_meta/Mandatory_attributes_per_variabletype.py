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


class Mandatory_attributes_per_variabletype(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on mandatory attributes according to variable types
    """

    def apply(self):

        mapvt = self.consmeta.get("mandatory_attributes_per_variabletype", {})
        for k, v in self.cfcollection:

            cftype = v.cftype
            cfattrs = v.attributesnames
            cfcate = v.cfcate

            mandatoryattributes = list(set(mapvt.get(cftype, {}).get(cfcate, [])).union(mapvt.get(cftype, {}).get("All", [])))

            if len(mandatoryattributes) > 0:
                for attr in mandatoryattributes:
                    if attr not in cfattrs:
                        self.status = 0
                        self.logger.error("[%s]-Attribute [%s] is mandatory - Variable [%s] - Type [%s]", str(self.ref), str(attr), str(k), str(cftype))
