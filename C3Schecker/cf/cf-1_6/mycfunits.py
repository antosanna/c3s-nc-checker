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


# TODO 

import sys
import os
import cfreferences

class Units():
	
	def __init__(self,u=None):
		self.u = u 
		self.isudunits()


	def __repr__(self):
		return "<Unift %s>" % self.u

	def isudunits(self):
		if self.u:
			try:
				assert 1 == 1

			except Exception as e:
				raise ValueError("Udunits does not support: %s" % self.u)

	@property
	def islongitude(self):
		islon = self.u in cfreferences.cf_longitude_units()		
		return islon

	@property
	def islatitude(self):
		islat = self.u in cfreferences.cf_latitude_units()		
		return islat

	@property
	def ispressure(self):
		return False

	@property
	def islength(self):
		return False

	@property
	def isreftime(self):
		return False

	@property
	def istime(self):
		return False

	@property
	def isreftime(self):
		return False

	def equivalent(self, u2):
		return True



