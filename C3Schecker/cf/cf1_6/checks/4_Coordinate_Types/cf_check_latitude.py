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


class cf_check_latitude(Basiccheck):
	""" Inheritated from parent Basiccheck
	"""

	def apply(self):

		ref = "CFREF-ch4.1"

		for k,v in self.cfcollection.coordinate_variables.iteritems():
			if v.cfcate == "Y"  and v.units not in self.cfref.cf_latitude_units() :
						self.status = 0
						self.check_msgs_logger.error("[%s]- Latitude unit [%s] is not allowed for variable [%s]",str(ref), str( v.unit ), str( k ) )
						continue


			if v.cfcate == "Y"  and v.units != self.cfref.cf_latitude_units()[0]:
						self.check_msgs_logger.error("[%s]- Latitude unit is highly recommended for variable [%s]",str(ref), str(self.cfref.cf_recommended_latitude_units()[0]), str( k ) )
