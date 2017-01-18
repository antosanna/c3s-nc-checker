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

class Mandatory_dimensions(Basiccheck):
    """ Inheritated from parent Basiccheck     
        Apply checks on dimensions . Test is mandatory_dimensions exist
    """ 

    def apply(self):
    	
		md = [ str(d) for d in self.consmeta.get("mandatory_dimensions", [])]
		collectdims = [str(d) for d in self.cfcollection.dimensions.keys()]
		if not set(md).issubset(set(collectdims))  and len(md) > 0:
			self.status = 0
		   	self.logger.error("[%s]-NetCDF Dimensions should be %s  - currently %s ", str(self.ref) , str(md) , str(collectdims)   )
