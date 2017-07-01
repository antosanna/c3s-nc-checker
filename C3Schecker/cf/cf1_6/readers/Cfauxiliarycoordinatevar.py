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

from Cfbasicvar import Cfbasicvar
from Cflabelvar import Cflabelvar


class Cfauxiliarycoordinatevar(Cfbasicvar):
    """ Inheritated from parent Cfbasicvar
        Define a CF variable as an auxiliary coordinate variable 
    """

    @staticmethod
    def define(variables, logger):

        identifiedvars = {}

        for varname, varclass in variables.iteritems():

            attr = getattr(varclass, 'coordinates', None)

            if attr:
                for name in attr.split():

                    try:
                        # if fct.is_string(variables[name]):
                        #     comment = "This is a CF Label Variable"
                        #     klass = Cflabelvar(str(name), variables[str(name)])
                        #     klass.comment = comment
                        #     identifiedvars[name] = klass
                        # else:
                            comment = "This is a CF Auxiliary Variable"
                            klass = Cfauxiliarycoordinatevar(str(name), variables[str(name)])
                            klass.comment = comment
                            identifiedvars[name] = klass
                    except:
                        pass

        return identifiedvars
