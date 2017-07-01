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


class Mandatory_data_minmax(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks for mandatory data minimum and maximum (can be used for global fields)
    """

    def apply(self):

        self.addinfo = "DataCheck"

        for k, v in self.cfcollection.data_variables.iteritems():

            datavariables_checks = self.consdata.get("default", {})
            datavariables_tocheck = (self.consdata.get(k, {})) 


            if bool(datavariables_tocheck):
                datavariables_checks = datavariables_tocheck

            mandatoryminmax = datavariables_checks.get("mandatory_min_max", "")

            if bool(mandatoryminmax):

                for x, y in mandatoryminmax.iteritems():
                    res = []

                    vv = self.cfcollection[x]
                    values = vv.netcdfinit[:]
                    valuesminmax = [values.min(), values.max()]
                    res = [i for i, j in zip(valuesminmax, y) if i != j]

                    if len(res) > 0:
                        self.status = 0
                        self.logger.error("[%s]- [%s] minimum and maximum values must be %s  - Currently %s", str(self.getcheckname(self.addinfo)), str(x), str(y), str(valuesminmax))

