#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: C. BERGERON -
#
# Note: None
#
#
#(C) Copyright 1996-2016 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#
 
import sys
 


class CFcellmethod():
	"""
		This class should generate the following dict from a cell_methods string:
		{
			"statements": [
			      { "statement_num":  1 ,"dimensions": ["lat"] , "method": "mean" , "where":"", "within":"", "over":"", "intervals": {"value": 1,"unit": "h"} , "comments": [texttext] }
			    ]
		}
	"""
 
	def __init__(self):
 
		self.cm_dict	= {}


	def __repr__(self):

		return str( self.cm_dict )


	def parse_cellmethods(self,cm):

		self.cm_dict["cell_methods attribute"] = str(cm)
		self.cm_dict["statements"] = []

		cm = cm.replace("("," ( ").replace(")"," ) ").lower().split()

		statementnum = 0
		i = 0 
		skip=0
		tmpstmt = {}

		for i in range(0,len(cm)):

			if skip > 0:
				skip = skip - 1
 				continue

 			if not cm[0] .endswith(":"):
				print "The cell_methods must begin with the pattern [name:]"
				break


			try:
				assert str(cm[i]).endswith(":") 

				try: 
					assert str( cm[i-1] ).endswith(":")
					tmpstmt["names"].append(str(cm[i][:-1]))
					skip = 0

 				except:
						statementnum += 1
						if len(tmpstmt): self.cm_dict["statements"].append(tmpstmt)
						tmpstmt = {}
						tmpstmt["statement_num"] = str(statementnum) 
						tmpstmt["names"] = [str(cm[i][:-1])]
						skip = 0
 
				tmpstmt["comments"]= []
				tmpstmt["intervals"]= []
				tmpstmt["method"]= ""

				skip = 0

				continue

			except:
				pass

			try:
				assert cm[i] in ["within","where","over"]
				tmpstmt[str(cm[i])] = cm[i+1]
				skip = 1
				continue
			except:
				pass

			try:
 				assert cm[i] == "("
 				comment = []
				j=i+1

				while cm[j] != ")":
					try:
						assert cm[j] == "interval:"
						tmpstmt["intervals"].append( {"value": cm[j+1],"unit":cm[j+2]})
						j+=3
						skip = skip + 3
						continue
					except:
						if cm[j] != "comment:" : tmpstmt["comments"].append(cm[j])
						skip = skip + 1
						j+=1
						continue 
				# skip = j - i
				skip = skip + 1
				continue
			except:
				pass

			tmpstmt["method"]= str(cm[i])

		if len(tmpstmt): self.cm_dict["statements"].append(tmpstmt)


	@property
	def get_cm_dict(self):
		return self.cm_dict

	@property
	def get_cm_method_names(self):
		cmmns  = []
		for i in self.cm_dict["statements"]:
			try:
				cmmns.append(    ( i["method"],i["names"])  )
			except:
				continue
		return cmmns



	@property
	def get_methods(self):
		return [ n["method"] for n in self.cm_dict["statements"]  ]


	@property
	def get_names(self):
		names = []
		for  n in self.cm_dict["statements"]:
			names = names +  n["names"] 
		return names

	@property
	def get_comments(self):
		comments = []
		for  n in self.cm_dict["statements"]:
			comments = comments +  n["comments"] 
		return comments

	@property
	def get_intervals_units(self):
		intervals = []
		for  n in self.cm_dict["statements"]:
			intervals = intervals +  n["intervals"] 
		return  [ n["unit"] for n in intervals  ]

	@property
	def get_intervals_values(self):
		intervals = []
		for  n in self.cm_dict["statements"]:
			intervals = intervals +  n["intervals"] 
		return  [ n["value"] for n in intervals  ]




if __name__ == "__main__":

	cm_str =  str(  (" ").join(sys.argv[1:])    ) 
	ccm = CFcellmethod()
	ccm.parse_cellmethods(cm_str)

	print ccm


	# print ccm.get_cm_dict
	# print ccm.get_names
	# print ccm.get_comments
	# print ccm.get_intervals_units
	# print ccm.get_intervals_values





