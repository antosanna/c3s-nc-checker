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

from Basiccheck import Basiccheck

class cf_check_dimensionless_vertical(Basiccheck):
	""" Inheritated from parent Basiccheck     
	""" 

	def apply(self):

		ref = "CFREF-ch4.3"

		for k,v in self.cfcollection.coordinate_variables.iteritems():
			if  self.cf_isdimensionless_vertical_coordinates(v):

				if re.match( self.cfref.cf_dimensionless_vertical_coordinates()[v.standard_name], str(v.formula_terms) ) :
					pass
				else:
					self.status = 0
					self.check_msgs_logger.error("[%s]- Formula_term attribute not compliant with  dimensionless vertical variable [%s] definition",str(ref), str( k ) )
					continue					



