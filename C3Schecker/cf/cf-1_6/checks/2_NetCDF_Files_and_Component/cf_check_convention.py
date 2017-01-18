#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: C. BERGERON -
#
# Note: None
#
#
#(C) Copyright 1996-2016 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

from Basiccheck import Basiccheck

class cf_check_convention(Basiccheck):
	""" Inheritated from parent Basiccheck     
	""" 

	def apply(self):

		ref = "CFREF-ch2.6.1"

		if "CF-1.6" not in self.cfcollection.convention.split(" "):
			self.check_msgs_logger.error("[%s]- Convention identified as [%s] - CF-1.6 Excepted",str(ref), str(self.cfcollection.convention)  )
			self.status = 0

 