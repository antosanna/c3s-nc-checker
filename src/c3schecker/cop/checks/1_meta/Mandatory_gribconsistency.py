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

from ..Basiccpcheck import Basiccheck


class Mandatory_gribconsistency(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks for the grib code consistency
    """

    def apply(self):

        self.addinfo = "MetadataCheck"

        # loop sur les datavars si paramid on test
        for k, v in list(self.cfcollection.data_variables.items()):
            if v.mars_paramid:
                for info in ["units", "standard_name"]:
                    if v.__getattr__(info):
                        try:
                            cfinfo = self.consgrib.get_info(v.mars_paramid, info)
                            assert v.__getattr__(info) == cfinfo and cfinfo is not None
                        except:
                            self.status = 0
                            self.logger.error(
                                "[%s]-  Non consistency between mars_paramid [%s] [%s=%s] and  variable [%s] [%s=%s]",
                                str(self.getcheckname(self.addinfo)),
                                str(v.mars_paramid),
                                info,
                                cfinfo,
                                str(k),
                                info,
                                v.__getattr__(info),
                            )
