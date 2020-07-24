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

from .Cfbasicvar import Cfbasicvar
from .Cfdatavar import Cfdatavar
from .Cfcoordinatevar import Cfcoordinatevar


class Cfvariablescollection:
    """ This is a class collecting CF variables, global attributes and netcdf information
    """

    def __init__(self):

        self.fileformat = ""
        self.convention = ""
        self.dimensions = []
        self.global_attributes = {}
        self.cfvariables = {}

    def __iter__(self):
        return iter(list(self.cfvariables.items()))

    def __getitem__(self, value):
        return self.cfvariables[value]

    def addvar(self, cfvariable):
        self.cfvariables.update(cfvariable)

    def addglobal(self, cfglobal):
        self.global_attributes.update(cfglobal)

    def onevartype(self, cfvarclass):
        return {str(name): klass for name, klass in self if isinstance(klass, cfvarclass)}

    def onevartypenames(self, cftype):
        return [str(name) for name, klass in self if klass.cftype == cftype]

    def onevartypestdnames(self, cftype):
        return [str(klass.standard_name) for name, klass in self if klass.cftype == cftype]

    @property
    def allvarnames(self):
        return [str(name) for name, klass in self]

    @property
    def data_variables(self):
        return self.onevartype(Cfdatavar)

    @property
    def coordinate_variables(self):
        return self.onevartype(Cfcoordinatevar)

    @property
    def alldimensions(self):
        return [str(d) for d in list(self.dimensions.keys())]
