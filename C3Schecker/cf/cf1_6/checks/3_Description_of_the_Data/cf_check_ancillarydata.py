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


class cf_check_ancillarydata(Basiccheck):
    """ Inheritated from parent Basiccheck
    """

    def apply(self):

        ref = "CFREF-ch3.4"

        # The cf_interpreter has already checked if the corresponding variable existing
        #	Test only for the type string

        for k, v in self.cfcollection:
            if v.ancillary_variables:
                if not (isinstance(v.ancillary_variables, str)):
                    self.check_msgs_logger.error("[%s]- Ancillary_variables attribute [%s] must be a string for variable [%s]", str(ref), str(v.ancillary_variables), str(var))
                    self.status = 0
                else:
                    for var in v.ancillary_variables.split():
                        try:
                            self.cfcollection[var]
                        except:
                            self.check_msgs_logger.error("[%s]-Ancillary_variables attribute [%s] contain non existing  variable [%s]", str(ref), str(v.ancillary_variables), str(var))
                            self.status = 0
                            continue
