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
import re


class cf_check_naming_conventions(Basiccheck):
    """ Inheritated from parent Basiccheck
    """

    def apply(self):

        ref = "CFREF-ch2.3"

        rname = re.compile("[a-zA-Z][a-zA-Z0-9_]*")

        for k, v in self.cfcollection:
            # For variable Names
            if not rname.match(k):
                self.status = 0
                self.check_msgs_logger.error('[%s]- Variable [%s] has a wrong name syntax', str(ref), v.name)

            # For attribute Names
            for a, b in v.attributes_notexcluded:
                if not rname.match(a):
                    self.status = 0
                    self.check_msgs_logger.error('[%s]- Attribute [%s] has a wrong name syntax', str(ref), a)

