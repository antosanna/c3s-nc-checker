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

from C3Schecker.utils import functions as fct

from .Cfbasicvar import Cfbasicvar


class Cfancillaryvar(Cfbasicvar):
    """ Inheritated from parent Cfbasicvar
        Define a CF variable as a ancillary variable
    """

    @staticmethod
    def define(variables, logger):

        identifiedvars = {}
        comment = "This is a CF Ancillary Variable"

        for varname, varclass in list(variables.items()):

            attr = getattr(varclass, 'ancillary_variables', None)
            if attr:

                klass = Cfancillaryvar(varname, varclass)
                klass.comment = comment
                identifiedvars[varname] = klass

        return identifiedvars
