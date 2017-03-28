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

from C3Schecker.cf.cf1_6.checks.Basiccheck import Basiccheck


class cf_check_stdnames(Basiccheck):
    """ Inheritated from parent Basiccheck
    """

    def apply(self):

        ref = "CFREF-ch3.2/3.4"

        for k, v in self.cfcollection:

            if (not v.standard_name) and (not v.long_name) and (v.cftype not in ['Cfboundaryvar']):
                self.check_msgs_logger.warning("[%s]- Variable description with long_name or standard_name attribute is highly recommended for variable [%s]", str(ref), str(k))
                continue

            if v.standard_name:
                std_name, stn_name_modifier = self.cf_get_stdname(v.standard_name, k)

                try:
                    self.std_names[std_name] is not None
                except:
                    self.check_msgs_logger.warning("[%s]- Standard_name attribute [%s] not CF compliant for variable [%s]", str(ref), str(v.standard_name), str(k))
