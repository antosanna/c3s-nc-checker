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

class Basiccheck:


    def __init__(self, logger, status, ref, cfcollection, consmeta, consdata):
    	self.name      = self.__class__.__name__
    	self.logger    = logger
    	self.status    = status
    	self.ref       = ref + "-" + self.name

        self.cfcollection  = cfcollection
        self.consmeta       = consmeta
        self.consdata       = consdata

 
    def __repr__(self):
    	return "C3S Check Class: %s"  % (self.__class__.__name__)



    def apply(self,):
    	pass



	 
  
