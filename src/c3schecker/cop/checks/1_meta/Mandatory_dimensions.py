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


class Mandatory_dimensions(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on dimensions . Test is mandatory_dimensions exist
    """

    def apply(self):
        self.addinfo = "MetadataCheck"
        actual_dimensions = [str(d) for d in list(self.cfcollection.dimensions.keys())]
        expected_dimensions = [str(d) for d in self.consmeta["mandatory_dimensions"]]

        for mandatory_dim in expected_dimensions:
            if actual_dimensions.count(mandatory_dim) == 0:
                self.status = 0
                self.logger.error(
                    "[%s]-NetCDF Dimensions must contain %s  - currently %s ",
                    str(self.getcheckname(self.addinfo)),
                    str(expected_dimensions),
                    str(actual_dimensions),
                )
                break

        # Only test for authorized dimensions if the actual count of dimensions exceeds
        # the count of expected mandatory dimensions
        if len(actual_dimensions) > len(expected_dimensions):
            expected_authorized_dims = self.consmeta.get(
                "authorized_other_dimensions", []
            )
            if expected_authorized_dims:
                if all(
                    actual_dimensions.count(auth_dim) == 0
                    for auth_dim in expected_authorized_dims
                ):
                    self.status = 0
                    self.logger.error(
                        "[%s]-NetCDF Dimensions should be a subset of %s  - "
                        "currently %s ",
                        str(self.getcheckname(self.addinfo)),
                        str(expected_authorized_dims),
                        str(actual_dimensions),
                    )
