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


class Mandatory_global_attributes_content(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on global attribute content
    """

    def apply(self):
        self.addinfo = "MetadataCheck"
        expected = self.consmeta["mandatory_global_attributes_values"]
        for attr_name, expected_values in expected.items():
            actual_value = getattr(self.cfcollection, attr_name, None)
            if actual_value is not None:
                if actual_value not in expected_values:
                    self.status = 0
                    self.logger.error(
                        "[%s]-Global Attribute [%s] value is not allowed - "
                        "Should be one of %s - currently [%s]",
                        self.getcheckname(self.addinfo),
                        attr_name,
                        expected_values,
                        actual_value,
                    )
