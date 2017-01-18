# 
# C. BERGERON - ECMWF 2016
#
# Note:     This file correponds to version CF Convention v1.6
#           Installation needed: udunits package (Osx: brew install udunits)
# 

import os
import re
import numpy as np
import xml.etree.ElementTree as ElementTree


def cf_reference():
    return "[CFREF]  NetCDF Climate and Forecast (CF) Metadata conventions, Version 1.6,  5 December, 2011"

def cf_allowed_datatypes():

    cf_allowed_datatypes = [np.character,
                                np.dtype('c'),
                                np.dtype('b'),
                                np.dtype('i4'),
                                np.int32,
                                np.int64,
                                np.float32,
                                np.double
                            ]

    return cf_allowed_datatypes


def cf_Xaxis_standard_names():
    return ['longitude','projection_x_coordinate','grid_longitude']

def cf_Yaxis_standard_names():
    return ['latitude','projection_y_coordinate','grid_latitude']

def cf_Zaxis_standard_names():
    return ['atmosphere_ln_pressure_coordinate',
             'atmosphere_sigma_coordinate',
             'atmosphere_hybrid_sigma_pressure_coordinate',
             'atmosphere_hybrid_height_coordinate',
             'atmosphere_sleve_coordinate',
             'ocean_sigma_coordinate',
             'ocean_s_coordinate',
             'ocean_s_coordinate_g1',
             'ocean_s_coordinate_g2',
             'ocean_sigma_z_coordinate',
             'ocean_double_sigma_coordinate']

def cf_Zaxis_units():
    return ['level', 'layer' 'sigma_level']

def cf_Taxis_standard_names():
    return ['time','forecast_reference_time']
 
def cf_recommended_globals():
    return ['title','institution','source','history','references','comment']

    
def cf_deprecated_units():
    return ['level', 'layer', 'sigma_level']

def cf_latitude_units():
    # Index 0 is the recommended one
    return ['degrees_north','degree_north', 'degree_N', 'degrees_N', 'degreeN','degreesN']

def cf_longitude_units():
    # Index 0 is the recommended one
    return ['degrees_east','degree_east', 'degree_E', 'degrees_E', 'degreeE', 'degreesE']


def cf_standard_names():

    entries = {}
    tree = ElementTree.parse( os.path.join( os.path.dirname(__file__) , "resources/cf-standard-name-table.xml") )

    i=0
    for element in tree.iter('entry'):
        entries[ element.attrib["id"] ] = element.find("canonical_units").text

    return entries


def cf_standard_names_modifiers():
    """Contains modified unit. None means no unit modification (or at least equivalent)"""

    return    {
     "detection_minimum" : None,
     "number_of_observations" : "1",
     "standard_error" : None,
     "status_flag" : None
                }

def cf_dimensionless_vertical_coordinates():
    return { 
        "atmosphere_ln_pressure_coordinate"             :   "(p0): ([A-Za-z][A-Za-z0-9_]*) (lev): ([A-Za-z][A-Za-z0-9_]*)", # "p0: var1 lev: var2"
        "atmosphere_sigma_coordinate"                   :   "(sigma): ([A-Za-z][A-Za-z0-9_]*) (ps): ([A-Za-z][A-Za-z0-9_]*) (ptop): ([A-Za-z][A-Za-z0-9_]*)", # "sigma: var1 ps: var2 ptop: var3"
        "atmosphere_hybrid_sigma_pressure_coordinate"   :   "(a): ([A-Za-z][A-Za-z0-9_]*) (b): ([A-Za-z][A-Za-z0-9_]*) (ps): ([A-Za-z][A-Za-z0-9_]*) (p0): ([A-Za-z][A-Za-z0-9_]*)", # "a: var1 b: var2 ps: var3 p0: var4"
        "atmosphere_hybrid_height_coordinate"           :   "(a): ([A-Za-z][A-Za-z0-9_]*) (b): ([A-Za-z][A-Za-z0-9_]*) (orog): ([A-Za-z][A-Za-z0-9_]*)", # "a: var1 b: var2 orog: var3"
        "atmosphere_sleve_coordinate"                   :   "(a): ([A-Za-z][A-Za-z0-9_]*) (b1): ([A-Za-z][A-Za-z0-9_]*) (b2): ([A-Za-z][A-Za-z0-9_]*) (ztop): ([A-Za-z][A-Za-z0-9_]*) (zsurf1): ([A-Za-z][A-Za-z0-9_]*) (zsurf2): ([A-Za-z][A-Za-z0-9_]*)", # "a: var1 b1: var2 b2: var3 ztop: var4 zsurf1: var5 zsurf2: var6"
        "ocean_sigma_coordinate"                        :   "(sigma): ([A-Za-z][A-Za-z0-9_]*) (eta): ([A-Za-z][A-Za-z0-9_]*) (depth): ([A-Za-z][A-Za-z0-9_]*)",    # "sigma: var1 eta: var2 depth: var3"
        "ocean_s_coordinate"                            :   "(s): ([A-Za-z][A-Za-z0-9_]*) (eta): ([A-Za-z][A-Za-z0-9_]*) (depth): ([A-Za-z][A-Za-z0-9_]*) (a): ([A-Za-z][A-Za-z0-9_]*) (b): ([A-Za-z][A-Za-z0-9_]*) (depth_c): ([A-Za-z][A-Za-z0-9_]*)", # "s: var1 eta: var2 depth: var3 a: var4 b: var5 depth_c: var6"
        "ocean_sigma_z_coordinate"                      :   "(sigma): ([A-Za-z][A-Za-z0-9_]*) (eta): ([A-Za-z][A-Za-z0-9_]*) (depth): ([A-Za-z][A-Za-z0-9_]*) (depth_c): ([A-Za-z][A-Za-z0-9_]*) (nsigma): ([A-Za-z][A-Za-z0-9_]*) (zlev): ([A-Za-z][A-Za-z0-9_]*)", # "sigma: var1 eta: var2 depth: var3 depth_c: var4 nsigma: var5 zlev: var6"
        "ocean_double_sigma_coordinate"                 :   "(sigma): ([A-Za-z][A-Za-z0-9_]*) (depth): ([A-Za-z][A-Za-z0-9_]*) (z1): ([A-Za-z][A-Za-z0-9_]*) (z2): ([A-Za-z][A-Za-z0-9_]*) (a): ([A-Za-z][A-Za-z0-9_]*) (href): ([A-Za-z][A-Za-z0-9_]*) (k_c): ([A-Za-z][A-Za-z0-9_]*)" # "sigma: var1 depth: var2 z1: var3 z2: var4 a: var5 href: var6 k_c: var7"
        }

def cf_calendars():

    return ["gregorian","standard","proleptic_gregorian","noleap","365_day","all_leap","366_day","360_day","julian","none"]

def cf_positive_values():
    return ['up','down']

def cf_attributes():
    """S(tring)  N(umeric) D(ata variable type/non-coordinate) C(oordinate) G(lobal) variable"""

    cf_attrs={}
    cf_attrs['add_offset']=['N','D']
    cf_attrs['ancillary_variables']=['S','D']
    cf_attrs['axis']=['S','C']
    cf_attrs['bounds']=['S','C']
    cf_attrs['calendar']=['S','C']
    cf_attrs['cell_measures']=['S','D']
    cf_attrs['cell_methods']=['S','D']
    cf_attrs['climatology']=['S','C']
    cf_attrs['comment']=['S',('G','D')]
    cf_attrs['compress']=['S','C']
    cf_attrs['Conventions']=['S','G']
    cf_attrs['coordinates']=['S','D']
    cf_attrs['_FillValue']=['D','D']
    cf_attrs['flag_meanings']=['S','D']
    cf_attrs['flag_values']=['D','D']
    cf_attrs['formula_terms']=['S','C']
    cf_attrs['grid_mapping']=['S','D']
    cf_attrs['history']=['S','G']
    cf_attrs['institution']=['S',('G','D')]
    cf_attrs['leap_month']=['N','C']
    cf_attrs['leap_year']=['N','C']
    cf_attrs['long_name']=['S',('C','D')]
    cf_attrs['missing_value']=['D','D']
    cf_attrs['month_lengths']=['N','C']
    cf_attrs['positive']=['S','C']
    cf_attrs['references']=['S',('G','D')]
    cf_attrs['scale_factor']=['N','D']
    cf_attrs['source']=['S',('G','D')]
    cf_attrs['standard_error_multiplier']=['N','D']
    cf_attrs['standard_name']=['S',('C','D')]
    cf_attrs['title']=['S','G']
    cf_attrs['units']=['S',('C','D')]
    cf_attrs['valid_max']=['N',('C','D')]
    cf_attrs['valid_min']=['N',('C','D')]
    cf_attrs['valid_range']=['N',('C','D')]
    cf_attrs['flag_masks']=['D','D']
    cf_attrs['cf_role']=['S','C']
    cf_attrs['featureType']=['S','G']
    cf_attrs['instance_dimension']=['S','D']
    cf_attrs['sample_dimension']=['S','D']
  
    return cf_attrs



def cf_formulaterm_measure_pattern():
    return re.compile(r'''
                           \s*
                           (?P<lhs>[\w_]+)
                           \s*:\s*
                           (?P<rhs>[\w_]+)
                           \s*
                        ''', re.VERBOSE)




def cf_excluded_attributes():
    return set(['_FillValue', 'missing_value', 'scale_factor' , 'add_offset' ])



def cf_cell_methods():
    cf_methods = [
        "point",
        "sum",
        "maximum",
        "Maximum",
        "median",
        "Median",
        "mid_range",
        "minimum",
        "Minimum",
        "mean",
        "mode",
        "standard_deviation",
        "variance"
    ]
    return cf_methods
