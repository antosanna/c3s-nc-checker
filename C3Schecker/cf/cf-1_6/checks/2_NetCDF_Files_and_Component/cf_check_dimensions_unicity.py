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

class cf_check_dimensions_unicity(Basiccheck):
	""" Inheritated from parent Basiccheck     
	""" 

	def apply(self):

		ref = "CFREF-ch2.4"

		
		# Check that variable has non-repeated dimensions
		for k,v  in self.cfcollection:
			occurence_dimname = {}	

			for d in v.dimensions:
				try:
					occurence_dimname[ str(d).lower() ] += 1
				except:
					occurence_dimname[ str(d).lower() ] = 1
					continue
				if occurence_dimname[ str(d).lower() ] > 1:
					self.status = 0
					self.check_msgs_logger.error('[%s]- Variable [%s] has duplicated dimensions [%s]',str(ref), str(k) , str(d) )					


