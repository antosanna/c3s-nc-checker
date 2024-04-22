
*****************************
C3S NetCDF Compliance Checker
*****************************


System setup
------------

Clone the repository from Bitbucket and change to the checker's directory::

 git clone https://git.ecmwf.int/scm/sapp/c3s-nc-checker.git
 cd c3s-nc-checker

Option 1: Install in a conda environment
========================================

1. Create a Conda environment

::

 conda -V
 conda update conda
 conda create -n c3s-nc-checker -c conda-forge -y python=3.10
 conda env update -n c3s-nc-checker -f environment.yml
 conda activate c3s-nc-checker

2. Install the checker from

::

 python -m pip install .


Option 2: Install in a virtualenv
=================================

1. Create the virtualenv and installation directory

::

 virtualenv .venv
 source .venv/bin/activate

2. Update pip

::

 python -m pip install --upgrade pip

3. Install

::

 python -m pip install .

Or to install in editable mode::

 python -m pip install -e .



Command Line Usage
------------------------

::

 c3s-checker --help
 Usage: c3s-checker [OPTIONS] [INPUTS]...

  Check the input NetCDF files against a specified convention or set of
  constraints

  Options:
      -t, --tests TEXT                Specific test (s) to be run
      -f, --tests-family [c3s|cf|cerise|all]
                                      Specific group of tests to be run  [default:
                                      all]
      --constraints FILE              JSON file representing the constraints for
                                      the convention that the NetCDF file(s) must
                                      follow. If this is not given, The
                                      -C/--convention option is used to load a
                                      default constraint file embedded with the
                                      package (see the option's docs). Otherwise,
                                      the -C/--convention is ignored.
      --exceptions FILE               JSON file representing what kind of
                                      deviation from the constraints are
                                      authorized. If a test fails but that failure
                                      is specified in this file, the overall test
                                      result isn't affected.
      -C, --convention [C3S-0.1|C3S-0.2|C3S-0.3]
                                      The NetCDF convention to use for the test
                                      suite. This is used to load a default
                                      constraint file corresponding to the
                                      convention, and is ignored if the
                                      --constraints option is given.  [default:
                                      C3S-0.3]
      --json                          Print output in json format
      --score-threshold INTEGER RANGE
                                      The minimum score a file must have to be
                                      considered as passing all the checks
                                      (expressed as a percentage - i.e between 0
                                      and 100). For operational run the score
                                      should be 100  [default: 100; 0<=x<=100]
      --min-passing-files INTEGER RANGE
                                      The minimum number of files that must pass
                                      to consider the command as passing
                                      (expressed as a percentage - i.e between 0
                                      and 100) For operational runs all the files
                                      should have pass all the tests.  [default:
                                      100; 0<=x<=100]
      -v, --verbose                   Enables verbose mode
      -p, --operational               Run in operational mode, where any failed
                                      test makes the overall test fail
      -l, --list-tests                List the available tests that can be
                                      executed. Run this first if you want to
                                      select only a few tests to run
      --help                          Show this message and exit.
