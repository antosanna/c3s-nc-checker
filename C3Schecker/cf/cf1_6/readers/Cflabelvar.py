#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: C. BERGERON -
#
# Note: None
#
#
# (C) Copyright 1996-2016 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#
import numpy as np
from C3Schecker.utils import functions as fct

from Cfbasicvar import Cfbasicvar


class Cflabelvar(Cfbasicvar):
    """ Inheritated from parent Cfbasicvar
        Define a CF variable as a Label variable
    """

    @staticmethod
    def define(variables, collections, logger):

        identifiedvars = {}
        comment = "This is a CF label variable"

        for varname, varclass in variables.iteritems():

            if np.issubdtype(varclass.dtype, np.str):

                try:
                    klass = Cflabelvar(varname, varclass)
                    klass.comment = comment
                    identifiedvars[varname] = klass
                except:
                    pass

        return identifiedvars
