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
from ...Basiccpcheck import Basiccheck


class Mandatory_cf_convention(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks for CF convention
    """

    def apply(self):
        expected_convention = self.consmeta["mandatory_cf_convention"]
        if self.cfcollection.convention != expected_convention:
            self.status = 0
            self.logger.error(
                "[%s]-CF Convention [%s] is mandatory - currently [%s]",
                str(self.ref),
                str(expected_convention),
                str(self.cfcollection.convention),
            )
