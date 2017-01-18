#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: C. BERGERON -
#
# Note: None
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

from  cfunits import *

import cfunits
print cfunits._ut_are_convertible


# from cfunits import Units

class c3scfunits(Units):
			# self.t = Units(units=None, calendar=None, names=None, definition=None, _ut_unit=None)


	# def tt(self):
	# 	# t=Units(units=None, calendar=None, names=None, definition=None, _ut_unit=None)
	# 	u = Units
	# 	u.islength = self.islength
	# 	return u

	def islength(self):

		print self._ut_unit

		ut_unit = self._ut_unit
		if ut_unit is None:
			return False
        
		return bool( _ut_are_convertible(ut_unit, self._length_ut_unit))

# setattr(A_Class, 'method_b', fn)


if __name__ == "__main__":

    testclass = c3scfunits
    print testclass('days since 2000-12-1 03:00').isreftime

    print testclass('days since 2000-12-1 03:00').islength()



    # testclass.islength
    print testclass
