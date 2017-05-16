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


class cf_check_coordinates(Basiccheck):
    """ Inheritated from parent Basiccheck
    """

    def apply(self):

        ref = "CFREF-ch5"

        for k, v in self.cfcollection:

            if v.coordinates:
                coords = map(unicode.strip, v.coordinates.split())

                for v_coord_name in coords:
                    try:

                        v_coord = self.cfcollection[v_coord_name]

                    except:
                        self.status = 0
                        self.check_msgs_logger.error("[%s]- Auxilliary Coordinate [%s] declared for variable [%s] does not exist  ", str(ref), str(v_coord_name), str(k))
                        continue

                    if v_coord.cfcate == "X":

                        # if not len(v_coord.dimensions) == 2:
                        #     self.check_msgs_logger.warning(v_coord.dimensions)
                        #     self.check_msgs_logger.warning("[%s]- Auxilliary Coordinate [%s] not a 2-dimensional Auxilliary longitude  ", str(ref), str(v_coord_name))

                        if not set(v_coord.dimensions).issubset(set(v.dimensions)):
                            self.status = 0
                            self.check_msgs_logger.error("[%s]- 2-dimensional Auxilliary Coordinate [%s] dimensions not part of coordinate variable [%s] dimensions", str(ref), str(v_coord_name), str(k))

                    if v_coord.cfcate == "Y":
                        # if not len(v_coord.dimensions) == 2:
                        #     self.check_msgs_logger.warning("[%s]- Auxilliary Coordinate [%s] not a 2-dimensional Auxilliary latitude  ", str(ref), str(v_coord_name))

                        if not set(v_coord.dimensions).issubset(set(v.dimensions)):
                            self.status = 0
                            self.check_msgs_logger.error("[%s]- 2-dimensional Auxilliary Coordinate [%s] dimensions not part of coordinate variable [%s] dimensions", str(ref), str(v_coord_name), str(k))
