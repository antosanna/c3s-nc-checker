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
import importlib
import logging
import re
import types
import numpy as np

from C3Schecker.utils import functions as fct
from Getgribinfo import Getgribinfo

import json

reload(sys)
sys.setdefaultencoding('utf-8')


def manage_status(f):
    # decorator - stop checkings option
    def wrapper(self, *args, **kwargs):
        if not self.status and self.stop:
            raise Exception
        return f(self, *args, **kwargs)

    return wrapper


class Cpchecker:
    """ A class to Check the netCDF input file  Copernicus compliancy
    """

    def __init__(self, cfcollection, c3stype="", infolevel="INFO", stop=False, checks=[], ignorechecks=[], confdir=None, passedcheckinfo=False):

        __REF__ = "C3S"

        self.cfvariablescollection = cfcollection

        self.status = 1

        self.stop = stop

        self.passedcheckinfo = passedcheckinfo

        self.check_msgs_logger, self.check_msgs = fct.loggers(infolevel).get_logger()

        self.ref = __REF__

        self.c3stype = c3stype

        self.checks = checks
        self.ignorechecks = ignorechecks

        self.confdir = confdir

        self.cp_check_compliance()

    def manage_status(f):
        # decorator - stop checkings option
        def wrapper(self, *args, **kwargs):
            if not self.status and self.stop:
                raise Exception
            return f(self, *args, **kwargs)

        return wrapper

    @property
    def status(self):
        return self.status

    @property
    def messages(self):

        return self.check_msgs.getvalue().split("\n")

    def cp_get_cons(self, category):


        dirc = str( os.path.dirname(__file__) + "/" + str(self.c3stype))

        if self.confdir != None:
            if os.path.isdir(self.confdir):
                dirc = self.confdir


        try:
            cp_cons_json = os.path.join( str(dirc), "cp_" + category + "_constraints.json")
            cp_cons = json.loads(open(cp_cons_json).read())
            return cp_cons
        except Exception as e:

            self.check_msgs_logger.error("Checking Stopped - Cannot read JSON %s %s constraints file, %s,  ", str(cp_cons_json), str(category), str(e))
            return {}

    def cp_get_gribcf(self):

        try:
            return Getgribinfo(self.c3stype,self.confdir)
        except Exception as e:
            self.check_msgs_logger.error("Checking Stopped - Problem with JSON grib to CF file, %s,  ", str(e))
            return {}

    @manage_status
    def cp_check_compliance(self):

        self.check_msgs_logger.staticinfo(1, " ")
        self.check_msgs_logger.staticinfo(1, " " + self.ref + " CHECKINGS:")
        self.check_msgs_logger.staticinfo(1, " --------------")
        self.check_msgs_logger.staticinfo(1, " ")

        self.cp_consmeta = self.cp_get_cons("meta")
        self.cp_consdata = self.cp_get_cons("data")
        self.cp_grib2cf = self.cp_get_gribcf()

        processed_checks = []
        available_checks = [str(f) for f in fct.get_immediate_filenames(os.path.join(os.path.dirname(__file__) + "/checks/"), ["__init__.py", "Basiccpcheck.py", "TemplateCheck.py"], "py")]

        if self.checks and len(self.checks) > 0:
            for c in self.checks.split(","):
                if c in available_checks:
                    processed_checks.append(c)
                else:
                    self.check_msgs_logger.error("Check [%s] is not existing ", str(c))
        else:
            processed_checks = available_checks

        if self.ignorechecks and len(self.ignorechecks) > 0:
            for c in self.ignorechecks.split(","):
                if c in available_checks:
                    processed_checks = list(set(processed_checks) - set([c]))
                else:
                    self.check_msgs_logger.error("Check [%s] is not existing, so it cannot be ignored ", str(c))

        try:  # exception will be triggered by the decorator to stop on error with option -s
            for pc in processed_checks:
                self.runcheck(pc)
        except Exception as e:
            self.check_msgs_logger.error("Checker stopped - [%s]", str(e))

    @manage_status
    def runcheck(self, modulepath):
        classname = modulepath.split(".")[-1]
        module = importlib.import_module("C3Schecker.cop.checks." + modulepath)
        checkclass = getattr(module, classname)(self.check_msgs_logger, self.status, self.ref, self.cfvariablescollection, self.cp_consmeta, self.cp_consdata, self.cp_grib2cf)
        checkclass.status = 1

        if self.passedcheckinfo:
            self.check_msgs_logger.checkinfo( str(classname) + ":")

        checkclass.apply()
        self.status = checkclass.status


        if not checkclass.status:
            self.status = checkclass.status


        if self.passedcheckinfo:
            self.check_msgs_logger.checkinfo( "       Status:" + str(self.status).replace("0","Failed").replace("1","passed") )
