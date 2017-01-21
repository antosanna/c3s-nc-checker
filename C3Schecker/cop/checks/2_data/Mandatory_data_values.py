#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: C. BERGERON -
#
# Note: None
#
#
#(C) Copyright 1996-2016 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

from Basiccpcheck import Basiccheck
import numpy


class Mandatory_data_values(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks for mandatory data in a list of values
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

            mandatorylov = datavariables_checks.get("mandatory_values", {})
            if bool(mandatorylov):

                for x, y in mandatorylov.iteritems():

                    try:
                        errorvalue = ""
                        vv = self.cfcollection[x]
                        values = vv.netcdfinit[:]
                        if values.ndim == 0:
                            values = [values]

                        if isinstance(values, numpy.ma.core.MaskedArray):  # work around when Netcdf4 var is a MaskedArray (get only unmasked values)
                            values = values.compressed()

                        for l in values:

                            if str(l) not in [str(i) for i in y]:  # dirty
                                errorvalue = str(l)
                                break

                        if errorvalue:
                            self.status = 0
                            self.logger.error("[%s]- [%s] values must be in %s  - Some other values has been found - First: %s  ", str(self.ref), str(x), str(y), str(len(values)))

                    except Exception as e:
                        self.status = 0
                        self.logger.error("[%s]- [%s] intervals must be %s  - Problem in the check (Could be: no variable [%s] found) %s ", str(self.ref), str(x), str(y), str(x), str(e))
                        continue
