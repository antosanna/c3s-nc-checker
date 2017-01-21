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

from Basiccpcheck import Basiccheck


class Mandatory_data_intervals(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks for mandatory data intervals
    """

    def apply(self):

        for k, v in self.cfcollection.data_variables.iteritems():

            datavariables_checks = self.consdata.get("default", {})
            try:
                datavariables_tocheck = (self.consdata.get(v.standard_name, {})).get(''.join(v.cell_methods.split()), {})
            except:
                datavariables_tocheck = ""

            if bool(datavariables_tocheck):
                datavariables_checks = datavariables_tocheck

            mandatoryintervals = datavariables_checks.get("mandatory_intervals", {})

            if bool(mandatoryintervals):
                for l, m in mandatoryintervals.iteritems():

                    try:
                        vv = self.cfcollection[l]
                        values = vv.netcdfinit[:]
                        valuesintervals = [(values[i - 1], x, x - values[i - 1]) for i, x in enumerate(values) if x - values[i - 1] != int(m)][1:]

                        if len(valuesintervals) > 0:
                            self.status = 0
                            self.logger.error("[%s]- [%s] intervals must be %s  - Some other intervals has been found - First: %s  ", str(self.ref),
                                              str(l), str(m), str(str(valuesintervals[0][0:2]) + "=interval " + str(valuesintervals[0][2])))

                    except:
                        self.status = 0
                        self.logger.error("[%s]- [%s] intervals must be %s  - Problem in the check (Could be: no variable [%s] found) ", str(self.ref), str(l), str(m), str(l))
                        continue
