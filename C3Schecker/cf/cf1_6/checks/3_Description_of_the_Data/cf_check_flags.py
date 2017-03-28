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

import re
import numpy as np

from C3Schecker.cf.cf1_6.checks.Basiccheck import Basiccheck


class cf_check_flags(Basiccheck):
    """ Inheritated from parent Basiccheck
    """

    def apply(self):

        ref = "CFREF-ch3.5"

        for k, v in self.cfcollection:
            fm = v.flag_meanings
            fv = v.flag_values
            fma = v.flag_masks

        # check mutual existences

            if fm is not None and (fv is None and fma is None):
                self.check_msgs_logger.error("[%s]- Flag_meanings attribute exists and no flag_values or flag_masks for variable [%s]", str(ref), str(k))
                self.status = 0
                continue

            if fm is None and (fv is not None or fma is not None):
                self.check_msgs_logger.error("[%s]- Flag_values or flag_masks exists and no flag_meanings for variable [%s]", str(ref), str(k))
                self.status = 0
                continue

            # against standard_name

            if v.standard_name:
                std_name, stn_name_modifier = self.cf_get_stdname(v.standard_name, k)
                if stn_name_modifier in [ i  for i in self.cfref.cf_standard_names_modifiers().keys() if 'flag' in i] \
                        and fm is None:
                    self.check_msgs_logger.error("S[%s]- tandard Name modified to a flag but flag_meanings does not exist for variable [%s]", str(ref), str(k))
                    self.status = 0
                    continue

            if fm is None and fv is None and fma is None:
                continue

        # check flag_meanings

            # check datatype
            if not (isinstance(fm, basestring)):
                self.status = 0
                self.check_msgs_logger.error("[%s]- Flag_meanings attribute [%s] must be a string for variable [%s]", str(ref), str(type(fm)), str(k))
                continue
            # check syntax
            fm_items = fm.split()
            rname = re.compile("^[0-9A-Za-z_\-@+.]+$")
            if len([i for i in fm_items if rname.match(str(i))]) != len(fm_items):
                self.status = 0
                self.check_msgs_logger.error("[%s]- Flag_meanings syntax incorrect for variable [%s]", str(ref), str(k))
                continue

        # check flag_values
            if fv is not None:
                # check datatype
                if (isinstance(fv, np.ndarray)):
                    pass
                elif (isinstance(fv, basestring)):  # not sure fully necessary- considering blank as separator
                    fv = map(str.strip, fv.split(' '))
                else:
                    self.status = 0
                    self.check_msgs_logger.error("[%s]- Flag_values must be a list for variable [%s]", str(ref), str(k))
                    continue

            isok = True
            for i in fv:
                if not  np.issubdtype(type(i),v.dtype.type):
                    self.status = 0
                    isok = False
                    self.check_msgs_logger.error("[%s]- Flag_values values must have the same type as variable [%s] [%s]", str(ref), str(k), str(v.dtype))
                    continue

            if not isok:
                continue

                # check number of values
            if len(fv) != len(fm_items):
                self.status = 0
                self.check_msgs_logger.error("[%s]- Flag_values must have the same number of values as flag_meanings for variable [%s]", str(ref), str(k))
                continue
                # check unicity
            if len(fv) != len(set(fv)):
                self.status = 0
                self.check_msgs_logger.error("[%s]- Flag_values values must be unique for variable [%s]", str(ref), str(k))
                continue

        # check flag_mask
            if fma is not None:

                # if not (isinstance(fma, np.ndarray)):
                #     self.status = 0
                #     self.check_msgs_logger.error("[%s]- Flag_values must be a list for variable [%s]", str(ref), str(k))
                #     continue

                if fma.dtype != v.dtype:
                    self.status = 0
                    self.check_msgs_logger.error("[%s]- Flag_masks values must have the same type as variable [%s] [%s]", str(ref), str(k), str(v.dtype))
                    continue

                if v.dtype not in [np.character, np.dtype('b'), np.dtype('i4'), np.int32]:
                    self.check_msgs_logger.error("[%s]- Variable [%s] type not appropriate for flag_masks:  [%s]", str(ref), str(k), str(v.dtype))
                    continue

                if len(fma) != len(fm_items):
                    self.status = 0
                    self.check_msgs_logger.error("[%s]- Flag_values must have the same number of values as flag_meanings for variable [%s]", str(ref), str(k))
                    continue

                if len([i for i in fma if i == 0]) != 0:
                    self.status = 0
                    self.check_msgs_logger.error("[%s]- Flag_values values must non-zero for variable [%s]", str(ref), str(k))
                    continue

            if fma is not None and fv is not None:
                bitwiseAND = all(map(lambda x, y: x & y == a, zip(fv, fma)))
                if not bitwiseAND:
                    self.status = 0
                    self.check_msgs_logger.error("[%s]- Bitwise AND of flag_values and flag_masks not equal to flag_value for variable [%s]", str(ref), str(k))
                    continue
