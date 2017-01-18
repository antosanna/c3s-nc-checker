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


class Cfdatavar(Cfbasicvar):
    """ Inheritated from parent Cfbasicvar
        Define a CF variable as a data variable
    """



    @staticmethod
    def define(variables, collections, logger):



        identifiedvars   = {}
        comment         = "This is a CF Data Variable"

        for varname, varclass in variables.iteritems():

            if varname not in collections.allvarnames:

                klass = Cfdatavar(varname, varclass)
                klass.cf_comment = comment
                collections.addvar({varname : klass })


        return identifiedvars
