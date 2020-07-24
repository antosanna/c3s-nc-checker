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


class cf_check_naming_unicity(Basiccheck):
    """ Inheritated from parent Basiccheck
    """

    def apply(self):

        ref = "CFREF-ch2.3"

        occurence_name = {}
        for k, v in self.cfcollection:
            try:
                occurence_name[str(k).lower()] += 1
            except:
                occurence_name[str(k).lower()] = 1
                continue

        for k, v in list(occurence_name.items()):
            if v > 1:
                self.status = 0
                self.check_msgs_logger.error('[%s]- Variable [%s] name is not unique: %s occurences found', str(ref), str(k), str(v))
