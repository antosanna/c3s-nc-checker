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

class TemplateCheck(Basiccheck):
	""" Please duplicate this class adding the class name and the check code
		Class variables to be used:
		-    self.collection : collection of CF variables
		- 	 self.consmeta  : Constraints regarding the metadata
		-    self.consdata  : Comstraints regarding the data 
		-    self.name 		: Name of the current class
		-    self.logger 	: Logger to get check log
		-    self.status 	: Status of the check ( 0: KO, 1: OK)
		-    self.ref 		: Reference of the check
	"""
 	
	def apply(self):
    	

		self.logger.error( "[%s]- Nothing to Check", self.ref   )
