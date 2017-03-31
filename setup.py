#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: C. BERGERON
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


import os

from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return open(file_path).read()


version = '0.1.1'


setup(
    name='C3Schecker',
    version=version,
    author='ECMWF',
    author_email='cedric.bergeron@ecmwf.int',
    license='Apache2.0',
    url='https://software.ecmwf.int/stash/projects/CDS/repos/checkers/browse/C3SChecker',
    description="Checker for C3S NetCDF files",
    long_description=read('README.rst'),
    packages=find_packages(),
    package_dir={'C3Schecker': 'C3Schecker'},
    include_package_data=True,
    install_requires=[
        'netCDF4==1.2.4',
        'cfunits',
        'numpy==1.10.2'
    ],
    classifiers=[
        'Development Status :: Alpha',
        'Intended Audience :: Data Analysts',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'License :: Apache 2.0',
        'Topic :: Scientific/Engineering :: Copernicus Climage Change Service',
    ],
    scripts=['bin/C3S_checker'],
    keywords='',
    entry_points={
        'console_scripts': [
            'C3Schecker = C3Schecker.cmd:main'
        ],
    },
)
