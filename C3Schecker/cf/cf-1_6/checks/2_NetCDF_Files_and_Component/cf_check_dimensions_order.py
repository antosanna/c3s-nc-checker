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

class cf_check_dimensions_order(Basiccheck):
	""" Inheritated from parent Basiccheck     
	""" 

	def apply(self):

		ref = "CFREF-ch2.4"

		recommended_dims_order = ['T','Z','Y','X'] 

		


		for k,v  in self.cfcollection:



  			if v.cftype  in ['Cfboundaryvar','Cfauxiliarycoordinatevar']:
				continue


			if len(v.dimensions) > 1:
				dims_type=[]
				dims_type_pos = []
				for d in v.dimensions:


					try:
						vd = self.cfcollection[str(d)] 
			
						dim_identify = vd.cfcate
						if dim_identify not in recommended_dims_order:
							self.check_msgs_logger.warning("[%s]- Dimension [%s] is not a space/time dimension for variable [%s] - [%s]" ,str(ref),   str(d) , str(k), str(vd.cate)   )
				
					except Exception as e:
						# self.check_msgs_logger.error("[%s]",str(e) )
						if not self.cf_is_dimension_reference_multidimentional(v,d):
							self.status = 0
							self.check_msgs_logger.error("[%s]- Dimension [%s] is not identifiable for variable [%s]" ,str(ref),   str(d) , str(k)   )
						else:
							self.check_msgs_logger.warning("[%s]- Variable [%s] is recommended to be defined" ,str(ref2),   str(d)  )
						dim_identify = None							


					dims_type.append(dim_identify)


				dims_type_pos = map (lambda x: recommended_dims_order.index(x) if x in recommended_dims_order else -1,  dims_type)

				

				if not list(set(dims_type_pos) - set([-1])) == sorted(list(set(dims_type_pos) - set([-1]))):
					self.check_msgs_logger.warning("[%s]- Space/time dimensions appear in T Z Y X order for variable [%s]: dimensions [%s] -- identified as: [%s], [%s]" ,str(ref),  str(k) , str(v.dimensions), str(dims_type), str( dims_type_pos ) ) 


				# Check if non space/time dimensions are not the left 
				if not len(set(dims_type_pos)) <= 1:
					for i in range(0,len(dims_type_pos) -1):
						if  dims_type_pos[i] != dims_type_pos[i+1]:
							x=i
							break

					if len( dims_type_pos[x:] ) != len( list(set(dims_type_pos) - set([-1])) ):
						self.check_msgs_logger.warning("[%s]- Some possible non space/time dimensions [%s]  are not on the left of Space/time dimensions for var [%s]",str(ref), str(d) , str(k) )

				#todo: check trailing dimensions
