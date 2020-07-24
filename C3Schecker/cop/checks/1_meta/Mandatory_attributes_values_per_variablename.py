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


class Mandatory_attributes_values_per_variablename(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on mandatory attributes according to short names
    """

    def apply(self):

        self.addinfo = "MetadataCheck"

        mapv = self.consmeta.get("mandatory_attributes_values_per_variablename", {})

        # Some of the attribute values should be checked against a regular expression
        regex_special = ["cell_methods"]

        for k, v in self.cfcollection:

            # stdname = v.standard_name

            mandatoryattributes = mapv.get(k, {})
            cfattrs = v.attributesnames

            if len(mandatoryattributes) > 0:

                for attr in mandatoryattributes:
                    # self.logger.error( attr )
                    # self.logger.error( cfattrs )

                    if attr in cfattrs and (str(attr) not in regex_special):

                        err_flag = False
                        if isinstance(mandatoryattributes[attr], float):
                            if float(v.getncattr(attr)) != mandatoryattributes[attr]:
                                err_flag = True
                        elif isinstance(mandatoryattributes[attr], int):
                            if int(v.getncattr(attr)) != mandatoryattributes[attr]:
                                err_flag = True
                        elif v.getncattr(attr) != mandatoryattributes[attr]:
                            err_flag = True
                        if err_flag == True:
                            self.status = 0
                            self.logger.error(
                                "[%s]-Wrong [%s] value - Variable [%s]; [%s] expected but [%s] found ",
                                str(self.getcheckname(self.addinfo)),
                                str(attr),
                                str(k),
                                str(mandatoryattributes[attr]),
                                str(v.getncattr(attr)),
                            )

                    if (attr in cfattrs) and (str(attr) in regex_special):
                        if not re.match(mandatoryattributes[attr], v.getncattr(attr)):

                            self.status = 0
                            self.logger.error(
                                "[%s]-Wrong [%s] value - Variable [%s]; [%s] does not match [%s]",
                                str(self.getcheckname(self.addinfo)),
                                str(attr),
                                str(k),
                                str(mandatoryattributes[attr]),
                                str(v.getncattr(attr)),
                            )
