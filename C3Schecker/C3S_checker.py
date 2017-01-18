#!/usr/bin/env python
#
# C3S_checker.py checks  C3S NetCDF compliancy for the Climate Data Store
#
# AUTHOR: ECMWF - C. BERGERON
#
#(C) Copyright 1996-2016 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#



import sys, os
import argparse
import importlib

from C3Schecker.cop.Cpchecker import Cpchecker

from  C3Schecker.utils import functions as fct


__CFVERSION__	= ("CF-1.6","cf-1_6") #(CF version code, files directory)


__VERSION__  = "0.1"
__FAILURECODE__  = 0
__SUCCESSCODE__  = 1


def check(argv):



	parser = argparse.ArgumentParser(description='C3S NetCDF Compliancy Checker', epilog=" ")
	parser.add_argument('-V', '--version',
               action="version",
               version="%(prog)s " + str(__VERSION__),
               help="checker Version" )

	parser.add_argument('-v', '--verbose',
	    action="store_true",
	    help="verbose" )

	parser.add_argument('-d', '--infolevel',
		default="info",
	    action="store",
		choices=["info","warning","error"],
	    help="information level output" )


	l=set(fct.get_immediate_subdirectories( os.path.join( os.path.dirname(__file__) + "/cop/") ) ) - set(["checks"])
	parser.add_argument('-t', '--type',
		required=True,
	    action="store",
		choices=l,
	    help="type of dataset" + str(l)  )

	parser.add_argument('-c', '--cf',
	    action="store_true",
	    help="CF checkings ONLY" )

	parser.add_argument('-k', '--checks',
	    action="store",
	    help="optional list of checks - default [All]" )

	parser.add_argument('-i', '--ignorechecks',
	    action="store",
	    help="optional list of checks to ignore - default [None]" )

	parser.add_argument('-s', '--stop',
	    action="store_true",
	    help="stop on error" )

	parser.add_argument('inputfiles',
		nargs="+",
		action="store",
	    help="NetCDF files list separated by blank")

	args = parser.parse_args(argv)
	return run(args)


def run(args):
 	# Process the netcdf files - One by One
	# -------------------------------------

	all_status = []

	for f in args.inputfiles:
 		all_msg=[]
		# FIRST STEP: CF Reader/Checker

 		# Dynamic import, depending on the CF convention version

		module = importlib.import_module("C3Schecker.cf." + __CFVERSION__[1] + ".Cfchecker")
		cfcheckings = getattr(module, "Cfchecker" )(f, __CFVERSION__[0], args.infolevel,args.stop)


		try:
			cfstatus = cfcheckings.status
			cfmessgs = cfcheckings.messages
			cfcollec = cfcheckings.cfvariablescollection
		except:
			cfstatus=0


		all_status.append(cfstatus)
		display_messages(args.verbose,cfmessgs)






		# SECOND STEP: COPERNICUS Checkers
		if cfcollec and not args.cf:


			copcheckings = Cpchecker(cfcollec, args.type, args.infolevel, args.stop, args.checks, args.ignorechecks)

			copstatus = copcheckings.status
			copmessgs = copcheckings.messages

			all_status.append(copstatus)
			display_messages(args.verbose,copmessgs)




	if all(all_status):
		 return __SUCCESSCODE__

	return __FAILURECODE__



def display_messages(verbose,msgs):

		all_msg_c=[ m for m in msgs  if str.find(m,"CRITICAL") != -1 ]
		for m in all_msg_c:
				print str(m)

		if verbose:
			all_msg=sorted(msgs, key =lambda x: 1 if str.find(x,"INFO") != -1 or len(x.strip()) == 0 else -1,reverse=True)
			for m in all_msg:
					print str(m)








if __name__ == "__main__":
     sys.exit( check(  sys.argv[1:] )  )
