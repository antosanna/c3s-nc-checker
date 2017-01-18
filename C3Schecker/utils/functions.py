#!/usr/bin/env python
# -*- coding: utf-8 -*-
# C. BERGERON - ECMWF 2016
#
# Note:
#

import os
import sys
import logging
from cStringIO	import StringIO
import types
import numpy as np









class loggers():

	def __init__(self,infolevel):

		self.infolevel = infolevel

		self.log_stream = StringIO()
		self.logger = logging.getLogger()

		self.define_logger()


	@property
	def levels(self):

		levels = {'CRITICAL' : logging.CRITICAL,
			'ERROR' : logging.ERROR,
			'WARNING' : logging.WARNING,
			'INFO' : logging.INFO,
			'DEBUG' : logging.DEBUG
			}
		return levels


	def get_logger(self):
		return self.logger, self.log_stream


	def define_logger(self):


		def log_staticinfo(self, numline=1, msg=""):

			self.removeHandler(self.console_handler)
			self.addHandler(self.blank_handler)
			for i in range(numline):
				self.info(msg)

			self.removeHandler(self.blank_handler)
			self.addHandler(self.console_handler)

		levels = self.levels

		try:
			self.logger.setLevel(levels[self.infolevel.upper()])
		except:
			self.logger.setLevel(levels["INFO"])


		console_handler = logging.StreamHandler(self.log_stream)
		console_handler.setFormatter(logging.Formatter("%(asctime)s.%(msecs)03d  - %(levelname)10s - %(message)s", datefmt="%H:%M:%S" ))

		blank_handler = logging.StreamHandler(self.log_stream)
		blank_handler.setFormatter(logging.Formatter("%(message)s"))

		self.logger.addHandler(console_handler)


		self.logger.console_handler = console_handler
		self.logger.blank_handler = blank_handler
		self.logger.staticinfo = types.MethodType(log_staticinfo, self.logger)



def get_immediate_subdirectories(a_dir):
    return [ name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name)) ]



def get_immediate_files(a_dir, excludefiles = [], extension = "*"):
	filelist=[]
	for path, subdirs, files in os.walk(a_dir):
			for name in files:
	 			if name.endswith("." + extension) and name not in excludefiles:
	 				filelist.append(     os.path.abspath(os.path.join(path, name)).replace(a_dir,"").replace(os.sep,".").replace("." + extension,"")   )

 	return filelist

def get_immediate_filenames(a_dir, excludefiles = [], extension = "*"):
	filelist=[]
	for path, subdirs, files in os.walk(a_dir):
			for name in files:
	 			if name.endswith("." + extension) and name not in excludefiles:
	 				filelist.append(     os.path.join(path, name).replace(a_dir,"").replace(os.sep,".").replace("." + extension,"")   )

 	return filelist


def get_immediate_fullpathfiles(a_dir, excludefiles=None, extension = "*"):
        if excludefiles is None:
                excludefiles = []

	filelist=[]
	for path, subdirs, files in os.walk(a_dir):
			for name in files:
	 			if name.endswith("." + extension) and name not in excludefiles:
	 				filelist.append(     os.path.abspath(os.path.join(path, name))  )

 	return filelist




def is_string(var):
    return np.issubdtype(var.dtype, np.str)

def truncate(string, width):
    if len(string) > width:
        string = string[:width-4] + ' ...'
    return string



def prRed(prt): print("\033[91m {}\033[00m" .format(prt))
def prRedBold(prt): print("\033[91m\033[1m {}\033[00m" .format(prt))
def prGreen(prt): print("\033[92m {}\033[00m" .format(prt))
def prGreenBold(prt): print("\033[92m\033[1m {}\033[00m" .format(prt))
def prYellow(prt): print("\033[93m {}\033[00m" .format(prt))
def prLightPurple(prt): print("\033[94m {}\033[00m" .format(prt))
def prPurple(prt): print("\033[95m {}\033[00m" .format(prt))
def prCyan(prt): print("\033[96m {}\033[00m" .format(prt))
def prLightGray(prt): print("\033[97m {}\033[00m" .format(prt))
def prBlack(prt): print("\033[98m {}\033[00m" .format(prt))
