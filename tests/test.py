#!/usr/bin/env python
#
#
# AUTHOR: ECMWF - C. BERGERON
#
# (C) Copyright 1996-2016 ECMWF.
#
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import argparse
import datetime
import os
import platform
import shutil
import sys
import tempfile

from cmd import main
from utils import functions as fct


class Checker_test:
    def __init__(self, keep):

        self.failed = 0
        self.keep = keep
        self.test_compliantfiles()
        self.test_noncompliantfiles()

    def get_failed(self):
        return self.failed

    def create_netcdffile(self, cdldir):
        """ run ncgen on cdl files contained in cdldir
                return the list of NetCDF filename and their temporary location"""

        listnc = []
        listcdl = fct.get_immediate_fullpathfiles(
            os.path.join(os.path.dirname(os.path.realpath(__file__)) + cdldir),
            [],
            "cdl",
        )

        tmpdir = tempfile.mkdtemp(dir="/tmp")
        print("")

        for f in listcdl:
            ncfile = tmpdir + os.sep + f.split(os.sep)[-1].replace("cdl", "nc")

            try:
                command = "ncgen -k 4 -o " + ncfile + " " + f
                os.popen(command)
                fct.prBlack(
                    "Creation of temporary NetCDF file: " + ncfile + " from " + f
                )
                listnc.append(ncfile)
            except:
                continue

        return listnc, tmpdir

    def test_compliantfiles(self):

        cdldirmain = "/tests/data/compliant/"
        listsubdir = fct.get_immediate_subdirectories(
            os.path.join(os.path.dirname(os.path.realpath(__file__))) + cdldirmain
        )

        for subdir in listsubdir:

            listnc, tmpdir = self.create_netcdffile(cdldirmain + subdir)
            print("")

            for ncfile in listnc:

                status = main(["-t", subdir, ncfile])
                fct.prBlack(
                    "Check " + ncfile + " with configuration [" + subdir.upper() + "]"
                )
                try:
                    assert status == 1
                    print((subdir + ncfile))
                    fct.prGreen(" PASSED - Checker status is 1 (Successful)")
                except:
                    self.failed += 1
                    fct.prRed(" FAILED - Checker status should be 1 (Successful)")

            if not (self.keep):
                shutil.rmtree(tmpdir)
                print("Temporary files deleted")

    def test_noncompliantfiles(self):

        cdldirmain = "/tests/data/non_compliant/"
        listsubdir = fct.get_immediate_subdirectories(
            os.path.join(os.path.dirname(os.path.realpath(__file__))) + cdldirmain
        )

        for subdir in listsubdir:

            listnc, tmpdir = self.create_netcdffile(cdldirmain + subdir)
            print()
            for ncfile in listnc:

                status = main(["-t", subdir, ncfile])
                print(
                    ("Check " + ncfile + " with configuration [" + subdir.upper() + "]")
                )
                try:
                    assert status == 0
                    fct.prGreen(" PASSED - Checker status is 1 (Unsuccessful)")

                except:
                    self.failed += 1
                    fct.prRed(" FAILED - Checker status should be 0 (Unsuccessful)")

            shutil.rmtree(tmpdir)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="", epilog=" ")

    parser.add_argument(
        "-k", "--keep", action="store_true", help="Do not remove temporary files"
    )
    args = parser.parse_args(sys.argv[1:])

    a = datetime.datetime.now()
    fct.prGreen("========== Test session start - " + str(a) + "=========")

    fct.prCyan("Plateform: " + str(platform.system()) + " - " + str(platform.version()))
    fct.prCyan("Python: " + str(platform.python_version()))

    failed = Checker_test(args.keep).get_failed()

    b = datetime.datetime.now()
    c = b - a
    e = divmod(c.days * 86400 + c.seconds, 60)

    if failed > 0:
        fct.prRedBold("Something Wrong")
        fct.prRed(
            "========== Test session end - Elapsed time : "
            + str(e[0])
            + " minutes "
            + str(e[1])
            + "seconds ==========="
        )

    else:
        fct.prGreenBold("Tests OK")
        fct.prGreen(
            "========== Test session end - Elapsed time : "
            + str(e[0])
            + " minutes "
            + str(e[1])
            + "seconds ==========="
        )
