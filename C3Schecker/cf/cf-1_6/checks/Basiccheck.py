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


    def __init__(self, logger, status, cfref, collection, cfuni , std_names):
    	self.name = self.__class__.__name__
        
    	self.check_msgs_logger = logger

    	self.status = status
        self.cfref = cfref
        self.cfcollection = collection
        self.cfuni = cfuni
        self.std_names = std_names

    def __repr__(self):
    	return "C3S Check Class: %s"  % (self.__class__.__name__)


    def apply(self):
    	pass





    def cf_get_stdname(self, stdname, var):

        std_name            = stdname
        std_name_modifier   = None

        # test it is a string 
        if not ( isinstance( std_name, basestring) ):
            self.check_msgs_logger.error("[%s]- Standard name attribute [%s] must be a string for variable [%s]",str(ref), str(std_name), str( var ) )
            self.status = 0
            return (None, None)


        if ' ' in std_name:
            std_name, std_name_modifier = map(str.strip, stdname.split(' ', 1))

            if std_name_modifier in self.cfref.cf_standard_names_modifiers():
                return ( std_name, std_name_modifier )
            else:
                self.check_msgs_logger.error("[%s]- Standard name attribute [%s] contains a invalid modifier [%s] for variable [%s]",str(ref), str(std_name), str(std_name_modifier), str( var ) )
                self.status = 0 
                return (None, None)

        return ( std_name, None )

	 
  
    def cf_isdimensionless_vertical_coordinates(self,v):
        
        if v.standard_name and v.standard_name in self.cfref.cf_dimensionless_vertical_coordinates().keys() :
            return True
        return False    

    def cf_is_dimension_reference_multidimentional(self,v,dim):
        # Test if a dimension reference a multi dimensional coordinate
        if v.coordinates:
            coords = map( unicode.strip, v.coordinates.split() )
            exist = 0
            for v_coord_name in coords:
                try:
                        v_coord = self.cfcollection[v_coord_name]
                except:
                    return False

                if dim in v_coord.dimensions:
                    exist += 1
            if exist > 0:
                return True
        return False