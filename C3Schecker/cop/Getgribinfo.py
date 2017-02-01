#!/usr/bin/env python
#
# C3S_checker.py checks  C3S NetCDF compliancy for the Climate Data Store
#
# AUTHOR: ECMWF - C. BERGERON
#
# (C) Copyright 1996-2016 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

import os
import sys
import json


class Getgribinfo:

    def __init__(self, c3stype):

		self.c3stype = c3stype
		self.gribinfo = self.get_gribcf()


    def get_gribcf(self):

        cp_cons_json = os.path.join(os.path.dirname(__file__) + "/" + self.c3stype, "grib_to_cf.json")
        cp_cons = json.loads(open(cp_cons_json).read())

        return cp_cons
		
    def get_info(self, paramid, cfinfo):
        try:
			return self.gribinfo.get(str(paramid)).get("cf").get(cfinfo)
        except:
			return None


