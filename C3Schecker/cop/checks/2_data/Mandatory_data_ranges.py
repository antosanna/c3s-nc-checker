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

import numpy as np

from C3Schecker.cop.checks.Basiccpcheck import Basiccheck


class Mandatory_data_ranges(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks for mandatory data in a given range
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

            mandatoryrange = datavariables_checks.get("mandatory_ranges", {})

            if bool(mandatoryrange):

                for x, y in list(mandatoryrange.items()):

                    try:
                        vv = self.cfcollection[x]
                        values = vv.netcdfinit[:]

                        if values.ndim == 0:
                            values = np.array([values])
                        valuesoutofrange = np.where(
                            np.logical_or(values > y[1], values < y[0])
                        )

                        # if values a des NaN -> traiter le cas
                        # print str(y)

                        if valuesoutofrange[0].size > 0:
                            self.status = 0
                            self.logger.error(
                                "[%s]- [%s] range must be %s  - First %s",
                                str(self.getcheckname(self.addinfo)),
                                str(x),
                                str(y),
                                str(valuesoutofrange[0][0]),
                            )

                    except:
                        if default:
                            pass
                        else:
                            self.status = 0
                            self.logger.error(
                                "[%s]-  no variable [%s] found",
                                str(self.getcheckname(self.addinfo)),
                                str(x),
                            )
                            continue
