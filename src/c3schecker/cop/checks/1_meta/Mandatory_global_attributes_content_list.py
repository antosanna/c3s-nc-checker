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


class Mandatory_global_attributes_content_list(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on global attribute content list
    """

    def apply(self):
        self.addinfo = "MetadataCheck"
        expected = self.consmeta["mandatory_global_attributes_values_list"]
        for attr_name, attr_value in self.cfcollection.__dict__.items():
            expected_list_of_values = expected.get(attr_name, [])
            actual_list_of_values = [v.strip() for v in attr_value.split(",")]
            for expected_value in expected_list_of_values:
                if expected_value not in actual_list_of_values:
                    self.logger.error(
                        "[%s]-Global Attribute [%s] does not contain [%s]",
                        self.getcheckname(self.addinfo),
                        attr_name,
                        expected_value,
                    )
                    self.status = 0
