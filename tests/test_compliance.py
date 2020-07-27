import os
import subprocess
import tempfile

import pytest

from C3Schecker.cmd import main
from C3Schecker.utils.functions import get_immediate_fullpathfiles


def cdl_files(dname):
    cdl_dir = os.path.join(os.path.dirname(__file__), "data", dname)
    return get_immediate_fullpathfiles(cdl_dir, [], "cdl")


@pytest.fixture(params=cdl_files("compliant"))
def compliant_file(request):
    dname = tempfile.mkdtemp()
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
    check = main(["-t", "seasonal", compliant_file])
    assert check == 0
