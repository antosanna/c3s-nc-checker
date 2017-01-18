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

from Basiccpcheck import Basiccheck

class Mandatory_bounds(Basiccheck):
    """ Inheritated from parent Basiccheck     
        Apply checks for cell_methods
        - If cell_methods on a variable and method is valid and not point :
        - [name]_bounds must exist
    """ 

    def apply(self):

    	for k,v  in self.cfcollection:
    		if v.cell_methods:
    			for i in v.cmdict.get_cm_method_names:

	    			method = i[0]
	    			names  = i[1]
	    			if i[0] != "point":
	    				for n in names:
	    					bo = str(n) + "_bounds" 
	    					try: 
	    						assert bo in self.cfcollection.allvarnames
	    					except:
	    						self.status = 0
	    						self.logger.error("[%s] -Method [%s] in cell_methods, variable [%s], indicates that [%s] must exist. But variable [%s] can not be found", str(self.ref) , str(method), str(k), str(bo), str(bo)  )


	    					try: 
	    						assert "bounds" in  self.cfcollection.alldimensions 
	    					except:
	    						self.status = 0
	    						self.logger.error("[%s] -Method [%s] in cell_methods, variable [%s], indicates that dimension [bounds] must exist. But dimension can not be found", str(self.ref) , str(method), str(k)  )





