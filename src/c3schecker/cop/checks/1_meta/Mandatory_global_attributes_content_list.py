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


class Mandatory_global_attributes_content_list(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on global attribute content list
    """

    def apply(self):

        self.addinfo = "MetadataCheck"

        mgavl = self.consmeta.get("mandatory_global_attributes_values_list", {})

        for k, v in list(self.cfcollection.global_attributes.items()):

            mgavl_possiblevalues = [str(a) for a in mgavl.get(k, [])]
            if len(mgavl_possiblevalues) > 0:
                # Each item of the List Of Values must exit
                for i in mgavl_possiblevalues:
                    if i not in [str(a).strip() for a in v.split(",")]:
                        self.logger.error(
                            "[%s]-Global Attribute [%s] does not contain [%s]",
                            str(self.getcheckname(self.addinfo)),
                            str(k),
                            str(i),
                        )
                        self.status = 0
