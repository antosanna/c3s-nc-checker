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

from ... import Cfcellmethods


class cf_check_cell_methods(Basiccheck):
    """ Inheritated from parent Basiccheck
    """

    def apply(self):

        ref = "CFREF-ch7.3"

        for k, v in self.cfcollection:
            if v.cell_methods:
                cmstr = v.cell_methods
                try:
                    cfc = Cfcellmethods.CFcellmethod()
                    cfc.parse_cellmethods(cmstr)
                    v.cmdict = cfc

                    names = cfc.get_names
                    for n in names:

                        if (
                            (v.dimensions and n not in v.dimensions)
                            and (
                                n
                                not in list(
                                    self.cfcollection.coordinate_variables.keys()
                                )
                            )
                            and (n not in ["area"])
                        ):
                            self.status = 0
                            self.check_msgs_logger.error(
                                "[%s]- Error in Cell_methods attribute for variable %s. Name [%s] not referenced in variable dimensions|coordinate",
                                str(ref),
                                str(k),
                                str(n),
                            )
                        if not v.dimensions and (n not in ["area"] or self.std_names):
                            self.status = 0
                            self.check_msgs_logger.error(
                                "[%s]- Error in Cell_methods attribute for variable %s. Name [%s] not referenced in Std names and not [area]",
                                str(ref),
                                str(k),
                                str(n),
                            )

                    methods = cfc.get_methods
                    for m in methods:
                        if m not in self.cfref.cf_cell_methods():
                            self.status = 0
                            self.check_msgs_logger.error(
                                "[%s]- Error in Cell_methods attribute for variable %s. Method [%s] not referenced",
                                str(ref),
                                str(k),
                                str(m),
                            )

                    units = cfc.get_intervals_units
                    for u in units:
                        try:
                            unit = self.cfuni(u)
                        except:
                            self.status = 0
                            self.check_msgs_logger.error(
                                "[%s]- Error in Cell_methods attribute for variable %s. Interval unit [%s] is not recognized by UDUNITS2 library",
                                str(ref),
                                str(k),
                                str(u),
                            )
                            continue

                    units = cfc.get_intervals_values
                    for l in units:
                        try:
                            float(l)
                        except:
                            self.status = 0
                            self.check_msgs_logger.error(
                                "[%s]- Error in Cell_methods attribute for variable %s. Interval value [%s] is a not Number",
                                str(ref),
                                str(k),
                                str(l),
                            )
                            continue

                except Exception as e:
                    self.status = 0
                    self.check_msgs_logger.error(
                        "[%s]- Error in Parsing Cell_methods attribute: %s for variable %s - (%s)",
                        str(ref),
                        str(cmstr),
                        str(k),
                        str(e),
                    )
