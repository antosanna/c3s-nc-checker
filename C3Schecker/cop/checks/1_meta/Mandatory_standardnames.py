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


class Mandatory_standardnames(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks for mandatory variable names
    """

    def apply(self):

        mvn = self.consmeta.get("mandatory_standardnames", {})
        for cftype, mvnvars in mvn.iteritems():

            for mvnvar in mvnvars:
                if mvnvar not in str(self.cfcollection.onevartypestdnames(cftype)):
                    self.status = 0
                    self.logger.error("[%s]-Variable [%s] is missing", str(self.ref), str(mvnvar))
