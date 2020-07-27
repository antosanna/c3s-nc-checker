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

import importlib
import logging
import os

from ...utils import get_immediate_filenames, loggers, truncate

from . import Cfreader, cfreferences


def manage_status(f):
    # decorator - stop checkings option
    def wrapper(self, *args, **kwargs):
        if not self.status and self.stop:
            raise Exception
        return f(self, *args, **kwargs)

    return wrapper


class Cfchecker:
    """ A class to Check the netCDF input file and its CF compliancy
    """

    def __init__(
        self, cffilename, cfversion, infolevel="INFO", stop=False, passedcheckinfo=False
    ):

        self.cfreader = Cfreader

        self.cfversion = cfversion

        self.cffilename = cffilename

        self.status = 1

        self.stop = stop

        self.passedcheckinfo = passedcheckinfo

        self.cfcollection = None

        self.cfref = cfreferences

        self.check_msgs_logger, self.check_msgs = loggers(infolevel).get_logger()

        self.check_cfcompliance()

    @property
    def messages(self):
        return self.check_msgs.getvalue().split("\n")

    @property
    def cfvariablescollection(self):
        return self.cfcollection

    def check_cfcompliance(self):

        self.check_msgs_logger.staticinfo(1, " CF CHECKINGS:")
        self.check_msgs_logger.staticinfo(1, " -------------")
        self.check_msgs_logger.staticinfo(1, " ")

        # [CFREF] REFERENCES FILES

        # References

        # Udunits2
        try:
            from cfunits import Units

            self.cfuni = Units

        except Exception as e:
            from .Units import Units

            self.cfuni = Units
            self.check_msgs_logger.error(
                "A problem occured with Udunits2 library. Error: " + str(e)
            )

        # Standard_name
        try:
            self.std_names = self.cfref.cf_standard_names()
        except Exception as e:
            self.check_msgs_logger.critical(
                "A problem occured with the standard names loading [%s]", str(e)
            )
            return

        # Area_Type

        self.check_msgs_logger.staticinfo(
            1, "INFO: NetCDF read against CF Version:" + str(self.cfversion)
        )
        self.check_msgs_logger.staticinfo(
            1, "INFO:                   CF Reference:" + str(self.cfref.cf_reference())
        )

        # [CFREF] Chapter 2 : NetCDF Files and Components
        self.check_msgs_logger.staticinfo(1, " ")
        self.check_msgs_logger.info("Start Checking filename [%s]", self.cffilename)
        self.check_msgs_logger.staticinfo(1, " ")

        try:
            self.cfcollection = self.cf_check_file("CFREF-ch2.1")
            if self.cfcollection is None:
                return
        except Exception as e:
            self.cf_describe()
            self.check_msgs_logger.critical(
                "Checking stopped during file reading: %s", str(e)
            )

        # LOOP on all tests in
        processed_checks = []
        available_checks = [
            str(f)
            for f in get_immediate_filenames(
                os.path.join(os.path.dirname(__file__) + "/checks/"),
                ["Basiccheck.py", "__init__.py"],
                "py",
            )
        ]

        try:  # exception will be triggered by the decorator to stop on error with option -s

            for pc in available_checks:
                self.runcheck(pc)

        except Exception as e:
            self.check_msgs_logger.critical(
                "Checker stopped - [%s] because of check [%s]", str(e), str(pc)
            )

        try:
            self.cf_describe()

        except Exception as e:
            self.cf_describe()
            self.check_msgs_logger.critical("Checking Stopped %s", str(e))

    @manage_status
    def cf_check_file(self, ref):

        if not os.path.exists(self.cffilename):
            self.status = 0
            self.check_msgs_logger.error(
                "[%s]- File [%s] not found", str(ref), self.cffilename
            )
            return None
        else:
            if not self.cffilename.endswith(".nc"):
                self.status = 0
                self.check_msgs_logger.error(
                    "[%s]- File [%s] does not have the extension .nc",
                    str(ref),
                    self.cffilename,
                )
                return None

        # Read Netcdf File
        try:
            cfreader = self.cfreader.Cfreader(self.cffilename, self.check_msgs_logger)
            cfcollect = cfreader.cfvariablescollection
        except Exception as e:
            status = 0
            self.check_msgs_logger.error("The CF NetCDF file cannot be read: " + str(e))
            return None

        return cfcollect

    def cf_is_dimension_reference_multidimentional(self, v, dim):
        # Test if a dimension reference a multi dimensional coordinate
        if v.coordinates:
            coords = list(map(str.strip, v.coordinates.split()))
            exist = 0
            for v_coord_name in coords:
                try:
                    v_coord = self.cfcollection[v_coord_name]
                except:
                    return False

                if dim in v_coord.dimensions:
                    exist += 1
            if exist > 0:
                return True
        return False

    def cf_describe(self):

        # Log netCDF Interpreted Information
        try:
            self.check_msgs_logger.info(
                "File Format     : [%s]", self.cfcollection.fileformat
            )
            self.check_msgs_logger.info(
                "     Convention : [%s]", self.cfcollection.convention
            )

            if self.check_msgs_logger.getEffectiveLevel() == logging.INFO:
                self.check_msgs_logger.staticinfo(1, " ")
            self.check_msgs_logger.info("Variables List --------------------- ")

            for k, v in self.cfcollection:
                if self.check_msgs_logger.getEffectiveLevel() == logging.INFO:
                    self.check_msgs_logger.staticinfo(1, " ")

                self.check_msgs_logger.info("  Variable Name   : [%s]", k)
                self.check_msgs_logger.info(
                    "           Dimensions            : [%s] ",
                    (",").join(map(str, v.dimensions)),
                )
                self.check_msgs_logger.info(
                    "           CF variable type      : [%s]", v.cftype
                )
                self.check_msgs_logger.info(
                    "           Checker comments      : [%s]", v.comment
                )
                self.check_msgs_logger.info(
                    "           Category              : [%s]", v.cfcate
                )
                self.check_msgs_logger.info(
                    "           Data Type             : [%s]", v.dtype
                )
                for a, b in v.attributes:
                    self.check_msgs_logger.info(
                        "              Attr   %s : [%s]",
                        "{:<20}".format("[" + a + "]"),
                        "".join(str(b).splitlines()),
                    )

            if self.check_msgs_logger.getEffectiveLevel() == logging.INFO:
                self.check_msgs_logger.staticinfo(1, " ")
            self.check_msgs_logger.info("Global Attribute List ---------------------")

            for k, v in list(self.cfcollection.global_attributes.items()):
                self.check_msgs_logger.info(
                    "  %s   : [%s]",
                    "{:<20}".format("[" + k + "]"),
                    truncate("".join(str(str(v).encode("utf-8")).splitlines()), 50),
                )

            self.check_msgs_logger.staticinfo(1, " ")

        except:

            self.check_msgs_logger.error("CF Describe Problem")

    @manage_status
    def runcheck(self, modulepath):
        classname = modulepath.split(".")[-1]
        module = importlib.import_module("c3schecker.cf.cf1_6.checks." + modulepath)
        checkclass = getattr(module, classname)(
            self.check_msgs_logger,
            self.status,
            self.cfref,
            self.cfcollection,
            self.cfuni,
            self.std_names,
        )

        if self.passedcheckinfo:
            self.check_msgs_logger.checkinfo(str(classname) + ":")

        checkclass.status = 1
        checkclass.apply()
        if not checkclass.status:
            self.status = checkclass.status

        if self.passedcheckinfo:
            self.check_msgs_logger.checkinfo(
                "       Status:"
                + str(self.status).replace("0", "Failed").replace("1", "passed")
            )
