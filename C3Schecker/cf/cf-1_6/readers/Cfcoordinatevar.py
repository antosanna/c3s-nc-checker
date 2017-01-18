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

from C3Schecker.utils import functions as fct

from Cfbasicvar import Cfbasicvar


class Cfcoordinatevar(Cfbasicvar):
    """ Inheritated from parent Cfbasicvar
        Define a CF variable as a coordinate variable
    """

    @staticmethod
    def define(variables, logger):

        identifiedvars   = {}
        comment         = "This is a CF Coordinate Variable"

        for  varname, varclass in variables.iteritems():

            if  ( (varclass.ndim == 0) or (varclass.ndim == 1 and varname in varclass.dimensions) ):

                klass = Cfcoordinatevar(varname, varclass)
                klass.comment = comment
                identifiedvars[varname] = klass

        return identifiedvars
