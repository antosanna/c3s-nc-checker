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

import re

from ..Basiccpcheck import Basiccheck


class Mandatory_global_attributes_content_pattern(Basiccheck):
    """ Inheritated from parent Basiccheck
        Apply checks on global attribute content list
    """

    def apply(self):
        self.addinfo = "MetadataCheck"
        expected = self.consmeta["mandatory_global_attributes_values_pattern"]
        for attr_name, attr_value in self.cfcollection.__dict__.items():
            expected_pattern = expected.get(attr_name)
            if expected_pattern is not None:
                if not re.match(expected_pattern, attr_value):
                    self.status = 0
                    self.logger.error(
                        "[%s]-Global Attribute [%s] value is not allowed - Incorrect "
                        "string pattern [%s] - It should be [%s]",
                        self.getcheckname(self.addinfo),
                        attr_name,
                        attr_value,
                        expected_pattern,
                    )
