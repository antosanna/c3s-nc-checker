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


class Mandatory_attributes_content(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on attribute contents
    """

    def apply(self):

        self.addinfo = "MetadataCheck"

        mac = self.consmeta.get("mandatory_attributes_values", {})

        for k, v in self.cfcollection:
            cfattrs = v.attributes

            for i, j in cfattrs:
                try:
                    possiblevalues = []
                    for val in mac.get(i):

                        try:
                            possiblevalues.append(float(val))
                        except:
                            possiblevalues.append(val)

                    if not (j in possiblevalues):
                        self.status = 0
                        self.logger.error(
                            "[%s]-Attribute [%s] [%s] value is not allowed - Variable [%s] - Should be one of %s ",
                            str(self.getcheckname(self.addinfo)),
                            str(i),
                            str(j),
                            str(k),
                            str(possiblevalues),
                        )

                except Exception as e:
                    pass
