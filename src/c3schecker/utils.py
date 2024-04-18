#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# AUTHOR: ECMWF - C. BERGERON
#
# (C) Copyright 1996-2017 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#


import logging
import os
import types
from io import StringIO
from itertools import chain, combinations

import numpy as np


def get_immediate_subdirectories(a_dir):
    return [
        name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))
    ]


def get_immediate_filenames(a_dir, excludefiles=[], extension="*"):
    filelist = []
    for path, subdirs, files in os.walk(a_dir):
        for name in files:
            if name.endswith("." + extension) and name not in excludefiles:
                filelist.append(
                    os.path.join(path, name)
                    .replace(a_dir, "")
                    .replace(os.sep, ".")
                    .replace("." + extension, "")
                )

    return filelist


def get_immediate_fullpathfiles(a_dir, excludefiles=None, extension="*"):
    if excludefiles is None:
        excludefiles = []

    filelist = []
    for path, subdirs, files in os.walk(a_dir):
        for name in files:
            if name.endswith("." + extension) and name not in excludefiles:
                filelist.append(os.path.abspath(os.path.join(path, name)))

    return filelist


def is_string(var):
    return np.issubdtype(var.dtype, np.str)


def truncate(string, width):
    if len(string) > width:
        string = string[: width - 4] + " ..."
    return string


def prRed(prt):
    print(("\033[91m {}\033[00m".format(prt)))


def prRedBold(prt):
    print(("\033[91m\033[1m {}\033[00m".format(prt)))


def prGreen(prt):
    print(("\033[92m {}\033[00m".format(prt)))


def prGreenBold(prt):
    print(("\033[92m\033[1m {}\033[00m".format(prt)))


def prYellow(prt):
    print(("\033[93m {}\033[00m".format(prt)))


def prLightPurple(prt):
    print(("\033[94m {}\033[00m".format(prt)))


def prPurple(prt):
    print(("\033[95m {}\033[00m".format(prt)))


def prCyan(prt):
    print(("\033[96m {}\033[00m".format(prt)))


def prLightGray(prt):
    print(("\033[97m {}\033[00m".format(prt)))


def prBlack(prt):
    print(("\033[98m {}\033[00m".format(prt)))


class Singleton(type):
    """Metaclass to make any class a singleton

    Credits: https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))
