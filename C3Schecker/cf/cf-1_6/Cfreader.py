#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: C. BERGERON -
#
# Note: The CF reader is inspired from
#       - Baudouin Raoult, ECMWF
#       - Iris cf lib, UK Met Office
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


import os

import netCDF4
import numpy as np

import cfreferences as cfref

from C3Schecker.utils import functions as fct

from readers.Cfvariablescollection  import Cfvariablescollection

from .readers.Cfbasicvar             import Cfbasicvar
from .readers.Cfcoordinatevar        import Cfcoordinatevar
from .readers.Cfboundaryvar          import Cfboundaryvar
from .readers.Cfancillaryvar         import Cfancillaryvar
from .readers.Cfauxiliarycoordinatevar import Cfauxiliarycoordinatevar
from .readers.Cfclimatologyvar       import Cfclimatologyvar
from .readers.Cfgridmappingvar       import Cfgridmappingvar
from .readers.Cfgridmappingvar       import Cfgridmappingvar
from .readers.Cflabelvar             import Cflabelvar
from .readers.Cfmeasurevar           import Cfmeasurevar
from .readers.Cfdatavar              import Cfdatavar



class Cfreader():
    """Read and classify the netCDF variables against given CF Convention"""

    def __init__(self, filename, logger):


        self.logger   = logger
        self.messages = []

        self.filename = filename

        self.cfvariablescollection = Cfvariablescollection()


        try:
            from  cfunits import Units
            self.cfuni = Units

        except Exception as e:
            from  mycfunits import Units
            self.cfuni = Units
            self.logger.error("A problem occured with Udunits2 library. Error: " + str(e))


        try:

            self.dataset = netCDF4.Dataset(filename, mode="r")
            self.variablesset = self.dataset.variables

        except Exception as e :
            self.logger.error( "For an unexpected reason, the file cannot be interpreted as a NetCDF dataset: " + str(e) )



        try:
            self.cfvariablescollection.fileformat = self.fileformat
            self.cfvariablescollection.convention = self.convention
            self.cfvariablescollection.dimensions = self.dimensions
            self.collect_cfvariables()
            self.interpret_cfcoordinates()

        except Exception as e:
            raise Exception("Netcdf Variable Classification - For an unexpected reason, the NetCDF file cannot be interpreted - Message: " + str(e) )



    @property
    def fileformat(self):
        return self.dataset.file_format



    @property
    def convention(self):
        try:
            convention = self.dataset.getncattr("Conventions")
        except:
            convention = "Not found"
        return convention

    @property
    def dimensions(self):
        return self.dataset.dimensions



    def collect_cfvariables(self):


        # Read Global attributes
        globalattributes = {attr: self.dataset.getncattr(attr) for attr in self.dataset.ncattrs()}
        self.cfvariablescollection.addglobal(globalattributes)


        # Get Coordinates Variables
        coordsvarcollected = Cfcoordinatevar.define(self.dataset.variables, self.logger)
        self.cfvariablescollection.addvar(coordsvarcollected)


        variablesset = self.dataset.variables.copy() # Clone without identified coordinates
        for k in list(self.cfvariablescollection.coordinate_variables.keys()):
             variablesset.pop(k, None)


        # Define non-Data and non-coordinate variables
        self.cfvariablescollection.addvar( Cfauxiliarycoordinatevar.define(self.dataset.variables, self.logger) )
        self.cfvariablescollection.addvar( Cfancillaryvar.define(variablesset, self.logger) )
        self.cfvariablescollection.addvar( Cfboundaryvar.define(self.dataset.variables, self.logger) )
        self.cfvariablescollection.addvar( Cfclimatologyvar.define(variablesset, self.logger) )
        self.cfvariablescollection.addvar( Cfgridmappingvar.define(variablesset, self.logger) )
        self.cfvariablescollection.addvar( Cfmeasurevar.define(variablesset, self.logger) )


        # Define the remained variables as Data
        self.cfvariablescollection.addvar( Cfdatavar.define(self.dataset.variables, self.cfvariablescollection, self.logger)  )




    def interpret_cfcoordinates(self):
        for k,v  in self.cfvariablescollection:

            self.cf_identify_dimension_type(v)

            if len(v.dimensions) == 0:
                v.cfcate = "Scalar"


    def cf_identify_dimension_type(self, d):

                def X(a,s,d):
                    # return X if and only if the coordinate is a CF X axis coordinate.

                    dim_type = None
                    if a == 'X':
                        dim_type = a
                    else:
                        possible_standard_name = cfref.cf_Xaxis_standard_names()
                        if  d.cfudunit.islongitude or (s in possible_standard_name):
                            dim_type = 'X'


                    return dim_type


                def Y(a,s,d):
                    # return Y if the coordinate is a CF Y axis coordinate.

                    dim_type = None

                    if a == 'Y':
                        dim_type = a
                    else:
                        possible_standard_name = cfref.cf_Yaxis_standard_names()
                        if  d.cfudunit.islatitude  or (s in possible_standard_name):
                            dim_type = 'Y'

                    return dim_type


                def Z(a,unit,s,p,d):
                    # return Z if the coordinate is a CF Z axis coordinate.

                    dim_type = None

                    if a == 'Z':
                        dim_type = a
                    else:
                        possible_standard_name  = cfref.cf_Zaxis_standard_names()
                        possible_specialunits   = cfref.cf_Zaxis_units()
                        if  (d.cfudunit.ispressure ) or (str(p).lower() in ['up','down']) or (s in possible_standard_name) or (u in possible_specialunits):
                            dim_type = "Z"

                    return dim_type


                def T(a,s,d):
                    # return T if the coordinate is a CF T axis coordinate.

                    dim_type = None

                    if a == 'T':
                        dim_type = a
                    else:
                        possible_standard_name  = cfref.cf_Taxis_standard_names()
                        if  ( d.cfudunit.isreftime or d.cfudunit.istime) or (s in possible_standard_name):
                            dim_type = 'T'

                    return dim_type

                a = d.axis
                u = d.units
                s = d.standard_name
                p = d.positive

                try:
                    unit = self.cfuni(u)
                except:
                    unit = self.cfuni()

                d.cfudunit = unit



                dim_types = [i for i in [ X(a,s,d), Y(a,s,d), Z(a,u,s,p,d), T(a,s,d)] if i is not None]

                

                d.cfcate = next(iter(dim_types), None)
                return d.cfcate
