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

 

class Mandatory_netcdf_format(Basiccheck):
    """ Inheritated from parent Basiccheck     
        Apply checks on netCDF format
    """ 


    def apply(self):
    	
		mnf = self.consmeta.get("mandatory_netcdf_format", None)

		if self.cfcollection.fileformat != mnf and mnf:
			self.status = 0
		   	self.logger.error("[%s]-File Format [%s] is mandatory - currently [%s]", str(self.ref) , str(mnf) , str(self.cfcollection.fileformat)   )

