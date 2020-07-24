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


class cf_check_time(Basiccheck):
    """ Inheritated from parent Basiccheck
	"""

    def apply(self):

        ref = "CFREF-ch3.4"

        for k, v in list(self.cfcollection.coordinate_variables.items()):
            if v.cfcate == "T":

                if not v.calendar:
                    self.check_msgs_logger.warning(
                        "[%s]- Calendar is recommended for the time coordinate variable [%s]",
                        str(ref),
                        str(k),
                    )
                    if not v.month_length:
                        self.check_msgs_logger.warning(
                            "[%s]- Month_length attribute is recommended when the calendar is not declared for the time coordinate variable [%s]",
                            str(ref),
                            str(k),
                        )

                    continue
                else:
                    if not (str(v.calendar) in self.cfref.cf_calendars()):
                        self.check_msgs_logger.warning(
                            "[%s]-Non standard calendar [%s] is  declared for the time coordinate variable [%s]",
                            str(ref),
                            str(v.calendar),
                            str(k),
                        )
                        if not v.month_length:
                            self.check_msgs_logger.warning(
                                "[%s]- Month_length attribute is recommended when the calendar is not standard for the time coordinate variable [%s]",
                                str(ref),
                                str(k),
                            )
