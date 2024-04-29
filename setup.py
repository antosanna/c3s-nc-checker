#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# AUTHOR: ECMWF - Adrien OYONO OWONO, Charalampos KARVELIS
#
# (C) Copyright 2020-2024 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#


import os

from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return open(file_path).read()


version = "0.1.0"


setup(
    name="c3schecker",
    version=version,
    author="ECMWF",
    author_email="adrien.owono@ecmwf.int",
    license="Apache2.0",
    url="https://git.ecmwf.int/projects/SAPP/repos/c3s-nc-checker/browse",
    description="Checker for NetCDF files",
    long_description=read("README.rst"),
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=read("requirements.txt").splitlines(),
    classifiers=[
        "Development Status :: Beta",
        "Intended Audience :: Data Analysts",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: Apache 2.0",
        "Topic :: Scientific/Engineering :: Copernicus Climate Change Service",
    ],
    keywords="",
    entry_points={"console_scripts": ["c3s-checker = c3schecker.cmd:main"]},
)
