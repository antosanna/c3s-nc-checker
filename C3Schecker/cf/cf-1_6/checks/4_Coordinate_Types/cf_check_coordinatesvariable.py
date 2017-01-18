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

class cf_check_coordinatesvariable(Basiccheck):
	""" Inheritated from parent Basiccheck     
	""" 

	def apply(self):

		ref = "CFREF-ch4"


		for k,v in self.cfcollection:

			if v.cftype  in ['Cfcoordinatevar','Cfauxiliarycoordinatevar']:

				if not v.units:
					if not self.cf_isdimensionless_vertical_coordinates(v):
						self.status = 0
						self.check_msgs_logger.error("[%s]- Unit is required for coordinates variable [%s]",str(ref), str( k ) )	
						continue # except dimensionless vertical coordinate

				else:
					unit_axis=""
					if v.positive and str(v.positive).lower() not in self.cfref.cf_positive_values():
						self.status = 0
						self.check_msgs_logger.error("[%s]- Positive attribute value not allowed for coordinates variable [%s]",str(ref), str( e) )	
						continue						

					try:
						unit = v.cfudunit
						if unit.ispressure or v.positive : unit_axis = "Z"
						if unit.islatitude: unit_axis = "Y"
						if unit.islongitude: unit_axis = "X"
						if unit.isreftime: unit_axis = "T"
 
					except Exception as e :
						if v.unit in self.cfref.cf_Zaxis_units():
							unit_axis = "Z"
						else:
							self.status = 0
							self.check_msgs_logger.error("[%s]- Unit not recognized for coordinates variable [%s]",str(ref), str( e) )	
							continue

				if v.axis:
					if v.axis not in ['X', 'Y', 'Z', 'T']:
						self.status = 0
						self.check_msgs_logger.error("[%s]- Axis contains not allowed value for variable [%s]",str(ref), str( k ) )
						continue					


					if unit_axis != v.axis:
						self.status = 0
						self.check_msgs_logger.error("[%s]- Axis [%s] value not consistent with unit [%s] for variable [%s]",str(ref), str(v.axis), str(v.units), str( k ) )
						continue						

			else:
				if v.axis:
						self.status = 0
						self.check_msgs_logger.error("[%s]- Axis attribute is not allowed for variable [%s]",str(ref), str( k ) )	
				if v.positive:
						self.status = 0
						self.check_msgs_logger.warning("[%s]- Positive attribute is not allowed for variable [%s]",str(ref), str( k ) )					
