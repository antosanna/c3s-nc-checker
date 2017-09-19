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

import numpy as np


class Mandatory_data_values(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks for mandatory data in a list of values
    """

    def apply(self):

        self.addinfo = "DataCheck"

        for k, v in self.cfcollection.data_variables.iteritems():

            default = True
            datavariables_checks = self.consdata.get("default", {})
            datavariables_tocheck = (self.consdata.get(k, {})) 


            if bool(datavariables_tocheck):
                datavariables_checks = datavariables_tocheck
                default = False

            mandatorylov = datavariables_checks.get("mandatory_values", {})
            if bool(mandatorylov):

                for x, y in mandatorylov.iteritems():


                    try:
                        errorvalue = ""
                        vv = self.cfcollection[x]
                        values = vv.netcdfinit[:]
                        if values.ndim == 0:
                            values = [values]

                        if isinstance(values, np.ma.core.MaskedArray):  # work around when Netcdf4 var is a MaskedArray (get only unmasked values)
                            values = values.compressed()

                        for l in values:
                            if l not in [i for i in y]:  # dirty -changed from string comparison
                                errorvalue = str(l)
                                break

                        if errorvalue:
                            self.status = 0
                            self.logger.error("[%s]- [%s] values must be in %s  - Some other values has been found - First: %s  ", str(self.getcheckname(self.addinfo)), str(x), str(y), str(len(values)))

                    except:
                        if default:
                            pass
                        else:
                            self.status = 0
                            self.logger.error("[%s]-  no variable [%s] found", str(self.getcheckname(self.addinfo)), str(x))
                            continue

