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


class Mandatory_data_intervals(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks for mandatory data intervals
    """

    def apply(self):

        self.addinfo = "DataCheck"

        for k, v in list(self.cfcollection.data_variables.items()):

            default = True
            datavariables_checks = self.consdata.get("default", {})
            datavariables_tocheck = self.consdata.get(k, {})

            if bool(datavariables_tocheck):
                datavariables_checks = datavariables_tocheck
                default = False

            mandatoryintervals = datavariables_checks.get("mandatory_intervals", {})

            if bool(mandatoryintervals):
                for l, m in list(mandatoryintervals.items()):

                    try:
                        vv = self.cfcollection[l]
                        values = vv.netcdfinit[:]
                        valuesintervals = [
                            (values[i - 1], x, x - values[i - 1])
                            for i, x in enumerate(values)
                            if x - values[i - 1] != int(m)
                        ][1:]

                        if len(valuesintervals) > 0:
                            self.status = 0
                            self.logger.error(
                                "[%s]- [%s] intervals must be %s  - Some other intervals has been found - First: %s  ",
                                str(self.getcheckname(self.addinfo)),
                                str(l),
                                str(m),
                                str(
                                    str(valuesintervals[0][0:2])
                                    + "=interval "
                                    + str(valuesintervals[0][2])
                                ),
                            )

                    except:
                        if default:
                            pass
                        else:
                            self.status = 0
                            self.logger.error(
                                "[%s]-  no variable [%s] found",
                                str(self.getcheckname(self.addinfo)),
                                str(l),
                            )
                            continue
