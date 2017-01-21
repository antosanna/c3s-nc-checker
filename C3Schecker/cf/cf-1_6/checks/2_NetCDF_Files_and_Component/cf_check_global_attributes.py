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

from Basiccheck import Basiccheck


class cf_check_global_attributes(Basiccheck):
    """ Inheritated from parent Basiccheck
    """

    def apply(self):

        ref = "CFREF-ch2.6.2"

        missing_gbls = []
        for g in self.cfref.cf_recommended_globals():
            missing = 1
            for k, v in self.cfcollection.global_attributes.iteritems():
                if k == g:
                    missing = 0
                    if not (isinstance(v, basestring)):
                        self.check_msgs_logger.error("[%s]- Global attribute [%s] type is not a String Type", str(ref), type(k))
            if missing:
                missing_gbls.append(g)
        if len(missing_gbls) > 0:
            self.check_msgs_logger.warning("[%s]- Missing recommended CF globals: [%s]", str(ref), str(', '.join(missing_gbls)))
