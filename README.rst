
*****************************
C3S NetCDF Compliance Checker
*****************************


System setup
------------
C3S_Checker makes use of Numpy, netCDF4-python, and Unidata udunits2 (> 2.2.17 ).

You need to make sure these dependencies are properly installed.

C:

http://www.unidata.ucar.edu/software/udunits/udunits-current/doc/udunits/udunits2.html#Binary


If you do not wish to install to the system Python, you can create a virtualenv
environment and install the checker and associated packages there:


Option 1: Install directly to your system
---------------------------------------

Update pip::
 pip install --upgrade pip

Create directory for checker::

 mkdir <code_dir>
 cd <code_dir>

To deploy the 'master' branch from the GIT repository::

 git clone ssh://git@git.ecmwf.int/sapp/c3s-nc-checker.git

Switch to checker directory::

 cd checker

Switch to master branch::

 git checkout master

Install dependencies if needed::

 pip install -r requirements.txt

Install Checker::

 python setup.py install


Option 2: Install to a conda virtual environment on your system
------------------------------------------------

Create Conda virtual environment::

 conda -V
 conda update conda
 conda create -n c3s-nc-checker -c conda-forge -y python=3.10
 conda env update -n c3s-nc-checker -f environment.yml
 conda activate c3s-nc-checker

Install Checker from git repository

 pip3 install git+ssh://git@git.ecmwf.int/sapp/c3s-nc-checker.git

Or from a specific git branch (e.g. cerise-refactoring)

 pip3 install git+ssh://git@git.ecmwf.int/sapp/c3s-nc-checker.git@cerise-refactoring


Option 3: Install to a virtualenv on your system
------------------------------------------------


Create Virtualenv and installation directory::

 virtualenv <install_dir>
 cd <install_dir>
 source bin/activate

Update pip::
 pip install --upgrade pip

Create directory for checker::

 mkdir <code_dir>
 cd <code_dir>

To deploy the 'master' branch from the GIT repository::

 git clone ssh://git@git.ecmwf.int/sapp/c3s-nc-checker.git

Switch to checker directory::

 cd checker

Switch to master branch::

 git checkout master

Install dependencies if needed::

 pip install -r requirements.txt

Install Checker::

 python setup.py install


Option 4: Install Checker in editable mode
------------------------------------------------

Install Checker in editable mode::

 python -m pip install -e .

Initial Test
------------

NOT YET IMPLEMENTED

Install Unidata NetCDF utilities -  ncgen should be properly installed and available.

Test with::

    ./tests/run_checkertests.py




Basic Command Line Usage
========================

::
 c3s-checker [-h] [-l] [-v] [-p] [-t {name of the test}] [-f {test family}] [--constraints {constraints file}] [--c3sexceptions {c3sexceptions file}] [--json] -C {convention} inputfiles [inputfiles ...]

Positional arguments::
----------------------
      inputfiles            NetCDF files list separated by blank

Optional arguments:
-------------------

*   -h, --help            show this help message and exit
*   -C, --convention      The NetCDF convention followed by the constraints file
*   -v, --verbose         Enables verbose mode
*   -t, --tests           Specific test to be run
*   -f, --tests_family    Specific group of tests to be run
*   --constraints         constraints file
*   --c3sexceptions       Specific C3S exceptions to be used
*   --json                Print output in json format
*   -p, --operational     Operational mode
*   -l, --tests_list      List of the available tests

