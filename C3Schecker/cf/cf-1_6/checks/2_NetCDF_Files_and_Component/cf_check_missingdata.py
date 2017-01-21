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

from Basiccheck import Basiccheck


class cf_check_missingdata(Basiccheck):
    """ Inheritated from parent Basiccheck
    """

    def apply(self):

        ref = "CFREF-ch2.5.1"

        rangemin, rangemax = None, None
        for k, v in self.cfcollection:
            # Check that valid_range and valid_min/max not both specified  - if so: error

            if (v.valid_min or v.valid_max) and v.valid_range:
                self.status = 0
                self.check_msgs_logger.error("[%s]- Valid_range and valid_min/valid_max are both specified for variable [%s]", str(ref), str(k))
            else:
                try:
                    rangemin, rangemax = v.valid_range
                except:
                    if v.valid_min:
                        rangemin = v.valid_min
                    if v.valid_max:
                        rangemax = v.valid_max

        # Check that fill value is not in the possible values range - if so: error
        # I consider that attribute valid_min or valid_max can not be present at the same time
            try:
                if v.fillvalue:
                    fillvalue = v.dtype(v.fillvalue)
                    if rangemin is not None and rangemax is not None:
                        if (fillvalue >= v.dtype(rangemin) and fillvalue <= v.dtype(rangemax)):
                            self.status = 0
                            self.check_msgs_logger.error("[%s]- Fillvalue [%s] in the range of possible values ([%s] - [%s]) for variable [%s]", str(ref), str(fillvalue), str(rangemin), str(rangemax), str(k))
                    elif rangemin is not None:
                        if (fillvalue >= v.dtype(rangemin)):
                            self.status = 0
                            self.check_msgs_logger.error("[%s]- Fillvalue [%s] in the range of possible values ([%s] - [%s]) for variable [%s]", str(ref), str(fillvalue), str(rangemin), str(rangemax), str(k))
                    elif rangemax is not None:
                        if (fillvalue <= v.dtype(rangemax)):
                            self.status = 0
                            self.check_msgs_logger.error("[%s]- Fillvalue [%s] in the range of possible values ([%s] - [%s]) for variable [%s]", str(ref), str(fillvalue), str(rangemin), str(rangemax), str(k))
            except:
                self.status = 0
                self.check_msgs_logger.error("[%s]- Fillvalue, Valid_min or Valid_max [%s] could be declared but not from the same variable datatype for variable [%s]", str(ref), str(fillvalue), str(rangemin), str(rangemax))
