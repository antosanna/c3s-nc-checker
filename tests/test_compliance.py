import os
import subprocess
import tempfile

import pytest

from C3Schecker import C3S_checker
from C3Schecker.utils.functions import get_immediate_fullpathfiles


def cdl_files(dname):
    cdl_dir = os.path.join(os.path.dirname(__file__), "data", dname)
    return get_immediate_fullpathfiles(cdl_dir, [], "cdl")


@pytest.yield_fixture(params=cdl_files("compliant"))
def compliant_file(request):
    dname = tempfile.mkdtemp()
    print(request.param)
    print(dir(C3S_checker))
    fname, _ = os.path.splitext(request.param)
    fname += ".nc"
    fname = fname.replace("/", "-")
    fname = os.path.join(dname, fname)

    cmdline = " ".join(["ncgen", "-k 4", "-o", fname, request.param])
    subprocess.check_call(cmdline, shell=True)

    yield fname

    if False:
        os.unlink(fname)


def test_foo(compliant_file):
    check = C3S_checker.check(["-t", "seasonal", compliant_file])
    assert check == 0
