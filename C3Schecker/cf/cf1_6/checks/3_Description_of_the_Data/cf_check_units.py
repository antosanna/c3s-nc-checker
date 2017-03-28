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

from C3Schecker.cf.cf1_6.checks.Basiccheck import Basiccheck


class cf_check_units(Basiccheck):
    """ Inheritated from parent Basiccheck
    """

    def apply(self):

        ref = "CFREF-ch3.1"

        for k, v in self.cfcollection:

            unit = self.cfuni
            v.cfudunit = unit

            # Apply except for CF Boundary Variables and CF Climatological Variables
            if v.cftype in ['Cfboundaryvar', 'Cfclimatologyvar', 'Cflabelvar', 'Cfgridmappingvar']:
                continue

            # Apply except Flags
            if v.flag_meanings or v.flag_marks or v.flag_values:
                continue

            if v.units:

                # MUST be string
                if not (isinstance(v.units, basestring)):
                    self.check_msgs_logger.error("[%s]- Units attribute [%s] must be a string for variable [%s]", str(ref), str(v.units), str(k))
                    self.status = 0
                    continue

                # Deprecated Units - just warning but may be rejected by udunits2ß
                if v.units in self.cfref.cf_deprecated_units():
                    self.check_msgs_logger.warning("[%s]- Units  attribute [%s] is deprecated for variable [%s]", str(ref), str(v.units), str(k))
                    continue
                # MUST be recognized by udunits
                try:
                    unit = self.cfuni(v.units)
                    v.cfudunit = unit
                except:
                    self.status = 0
                    self.check_msgs_logger.error("[%s]- Units  [%s] is not recognized by UDUNITS2 library for variable [%s]", str(ref), str(v.units), str(k))
                    continue

                # MUST be consistent with canonical unit from standard name (if exists)
                if v.standard_name:

                    try:
                        std_name, stn_name_modifier = self.cf_get_stdname(v.standard_name, k)

                        if stn_name_modifier:
                            if not self.cfref.cf_standard_names_modifiers[stn_name_modifier]:  # if a unit is specified for modification
                                std_unit = self.cfref.cf_standard_names_modifiers[stn_name_modifier]
                                std_unit_unit = self.cfuni(std_unit)
                        else:
                            std_unit = self.std_names[std_name]
                            std_unit_unit = self.cfuni(std_unit)  # udunit instance

                    except Exception as e:
                        self.status = 0
                        self.check_msgs_logger.warning("[%s]- Units cannot be compared with standard name canonical unit - Std name does not exist or canonical unit invalid [%s]", str(ref), str(e))
                        continue

                    if unit.isreftime:  # Reference Time remove
                        tmp = str(v.units).split()[0]
                        unit = self.cfuni(tmp)

                    if not (unit.equivalent(std_unit_unit)):
                        self.status = 0
                        self.check_msgs_logger.error("[%s]- Units [%s] not consistent with standard name canonical unit [%s] for variable [%s]", str(ref), unit, std_unit_unit, str(k))

            else:
                self.check_msgs_logger.warning("[%s]- Units attribute is required for variable [%s] unless the variable is dimensionless", str(ref), str(k))
