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

from .. import cfreferences as cfref


class Cfbasicvar:
    def __init__(self, variablename, variable):

        self.name = variablename

        self.netcdfinit = variable
        self.cftype = self.__class__.__name__
        self.comment = ""
        self.cfcate = ""
        self.cfudunit = None
        self.cmdict = None

        self.ncattrs = self.netcdfinit.ncattrs()

    def __getattr__(
        self, name
    ):  # add netcdf4 attributes (data object) to Cfbasicvar attributes
        return getattr(self.netcdfinit, name, None)

    def __repr__(self):
        return "%s([%r], [%r])" % (self.__class__.__name__, self.name, self.netcdfinit)

    @property
    def attributes(self):
        return ((attr, self.netcdfinit.getncattr(attr)) for attr in self.ncattrs)

    @property
    def attributesnames(self):
        return [attr for attr in self.ncattrs]

    @property
    def attributes_notexcluded(self):
        return (
            (attr, self.netcdfinit.getncattr(attr))
            for attr in (set(self.ncattrs) - set(cfref.cf_excluded_attributes()))
        )
