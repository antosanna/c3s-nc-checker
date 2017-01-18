
*****************************
C3S NetCDF Compliancy Checker 
*****************************



System setup
------------
C3S_Checker makes use of Numpy, netCDF4-python, and Unidata udunits2.
You have to make sure these dependencies are properly installed.

Python:

pip install --upgrade pip
pip install -r requirements.txt

C:

http://www.unidata.ucar.edu/software/udunits/udunits-current/doc/udunits/udunits2.html#Binary

Deploy
------

To deploy the 'master' branch from the GIT repository::

    git clone https://software.ecmwf.int/stash/scm/cds/C3SChecker.git



Install package
---------------

Install with::

    python setup.py install


Initial Test
------------

Install Unidata NetCDF utilities -  ncgen should be properly installed and available.

Test with::

    ./tests/run_checkertests.py




Basic Command Line Usage
========================

::
 ./C3S_checker.py [-h] [-V] [-v] [-d {info,warning,error}] -t{seasonal,nemo,...} [-c] [-k C3SCHECK] [-i C3SCHECK] [-s] inputfiles [inputfiles ...]

Positional arguments::
----------------------
      inputfiles            NetCDF files list separated by blank

Optional arguments:
-------------------

*   -h, --help            show this help message and exit
*   -V, --version         CF Version
*   -v, --verbose         Verbose
*   -d {info,warning,error}, --infolevel {info,warning,error} Information Level output
*   -t {seasonal,nemo}, --c3stype {seasonal,nemo} Type of Datasetset(['seasonal', 'nemo'])
*   -c, --cf              CF Checkings ONLY
*   -k C3SCHECK, --checks  Optional List of checks - Default [All]
*   -i C3SCHECK, --ignorechecks  Optional List of ignored checks - Default [None]
*   -s, --stop            Stop on error

