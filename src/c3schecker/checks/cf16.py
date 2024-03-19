import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from xml.etree import ElementTree
import logging

from cfunits import Units
from netCDF4 import Dataset
import numpy as np

from c3schecker.checks import register
from c3schecker.utils import Singleton, powerset
from pkg_resources import resource_filename

CONVENTION = "CF-1.6"


class UnknownStandardNameError(Exception):
    pass


class CFREF(metaclass=Singleton):
    data_types = (
        np.dtype("S1"),
        np.dtype("c"),
        np.dtype("b"),
        np.dtype("i4"),
        np.int32,
        np.int64,
        np.float32,
        np.double,
    )
    dimensions_order = ("*", "T", "Z", "Y", "X")
    time_axis_std_names = ("time", "forecast_reference_time")
    z_axis_std_names = (
        "atmosphere_ln_pressure_coordinate",
        "atmosphere_sigma_coordinate",
        "atmosphere_hybrid_sigma_pressure_coordinate",
        "atmosphere_hybrid_height_coordinate",
        "atmosphere_sleve_coordinate",
        "ocean_sigma_coordinate",
        "ocean_s_coordinate",
        "ocean_s_coordinate_g1",
        "ocean_s_coordinate_g2",
        "ocean_sigma_z_coordinate",
        "ocean_double_sigma_coordinate",
    )
    y_axis_std_names = ("latitude", "projection_y_coordinate", "grid_latitude")
    x_axis_std_names = ("longitude", "projection_x_coordinate", "grid_longitude")
    z_axis_units = ("level", "layer" "sigma_level")
    z_axis_orientations = ("up", "down")
    global_attrs = (
        "title",
        "institution",
        "source",
        "history",
        "references",
        "comment",
    )
    deprecated_units = ("level", "layer", "sigma_level")
    dimensionless_vertical_coordinates = {
        "atmosphere_ln_pressure_coordinate": re.compile(
            r"\s*p0\s*:\s*[\w_]+\s+lev\s*:\s*[\w_]+\s*"
        ),
        "atmosphere_sigma_coordinate": re.compile(
            r"\s*sigma\s*:\s*[\w_]+\s+ps\s*:\s*[\w_]+\s+ptop\s*:\s*[\w_]+\s*"
        ),
        "atmosphere_hybrid_sigma_pressure_coordinate": re.compile(
            r"\s*a\s*:\s*[\w_]+\s+b\s*:\s*[\w_]+\s+ps\s*:\s*[\w_]+\s+p0\s*:\s*[\w_]+\s*"
        ),
        "atmosphere_hybrid_height_coordinate": re.compile(
            r"\s*a\s*:\s*[\w_]+\s+b\s*:\s*[\w_]+\s+orog\s*:\s*[\w_]+\s*"
        ),
        "atmosphere_sleve_coordinate": re.compile(
            r"\s*a\s*:\s*[\w_]+\s+b1\s*:\s*[\w_]+\s+b2\s*:\s*[\w_]+\s+"
            r"ztop\s*:\s*[\w_]+\s+zsurf1\s*:\s*[\w_]+\s+zsurf2\s*:\s*[\w_]+\s*"
        ),
        "ocean_sigma_coordinate": re.compile(
            r"\s*sigma\s*:\s*[\w_]+\s+eta\s*:\s*[\w_]+\s+depth:\s*[\w_]+\s*"
        ),
        "ocean_s_coordinate": re.compile(
            r"\s*s\s*:\s*[\w_]+\s+eta\s*:\s*[\w_]+\s+depth:\s*[\w_]+\s+a:\s*[\w_]+\s+"
            r"b:\s*[\w_]+\s+depth_c:\s*[\w_]+\s*"
        ),
        "ocean_sigma_z_coordinate": re.compile(
            r"\s*sigma\s*:\s*[\w_]+\s+eta\s*:\s*[\w_]+\s+depth\s*:\s*[\w_]+\s+"
            r"depth_c\s*:\s*[\w_]+\s+nsigma\s*:\s*[\w_]+\s+zlev\s*:\s*[\w_]+\s*"
        ),
        "ocean_double_sigma_coordinate": re.compile(
            r"\s*sigma\s*:\s*[\w_]+\s+depth\s*:\s*[\w_]+\s+z1\s*:\s*[\w_]+\s+"
            r"z2\s*:\s*[\w_]+\s+a\s*:\s*[\w_]+\s+href\s*:\s*[\w_]+\s+"
            r"k_c\s*:\s*[\w_]+\s*"
        ),
    }
    cf_units_modifiers = {
        "detection_minimum": None,
        "number_of_observations": "1",
        "standard_error": None,
        "status_flag": None,
    }
    cf_recommended_latitude_unit = "degrees_north"
    cf_acceptable_latitude_units = (
        "degree_north",
        "degree_N",
        "degrees_N",
        "degreeN",
        "degreesN",
    )
    cf_recommended_longitude_unit = "degrees_east"
    cf_acceptable_longitude_units = (
        "degree_east",
        "degree_E",
        "degrees_E",
        "degreeE",
        "degreesE",
    )
    cf_calendars = (
        "gregorian",
        "standard",
        "proleptic_gregorian",
        "noleap",
        "365_day",
        "all_leap",
        "366_day",
        "360_day",
        "julian",
        "none",
    )
    #cf_cell_methods_pattern = re.compile(
    #    r"^((?P<name>(\s*area|[\w_]+:\s+)+)(?P<method>(point|sum|mean|maximum|minimum"
    #    r"|mid_range|standard_deviation|variance|mode|median)"
    #    r"(\s+where\s+[\w_-]+(\s+over\s+[\w_-]+)?)?"
    #    r"(\s+\((((interval:\s[0-9]+(\.[0-9]+)?\s([a-zA-Z_]+|1))"
    #    r"(\s+interval:\s[0-9]+(\.[0-9]+)?\s([a-zA-Z_]+|1))*"
    #    r"(\s+comment:(\s[\w_-]+)+)?)|(([\w_-]+\s*)+))\))?))*$",
    #    re.VERBOSE,
    #)

    cf_cell_methods_pattern = re.compile(r'^'
        r'(\s*\S+\s*:\s*(\S+\s*:\s*)*'
        r'([a-z_]+)'
        r'(\s+where\s+\S+(\s+over\s+\S+)?)?'
        r'(\s+(over|within)\s+(days|years))?\s*'
        r'(\((interval:\s+\d+\s+\S+\s*)*(comment: .+)?.*\))?)'
        r'+$'
        )



    __standard_names = None
    __std_names_tree = ElementTree.parse(
        resource_filename("c3schecker", "resources/cf-standard-name-table.xml")
    )

    def identify_dimension_type(self, dim_var):
        try:
            axis = dim_var.axis
            for axis_type in self.dimensions_order[1:]:
                if axis == axis_type:
                    return axis
        except AttributeError:
            pass
        try:
            std_name = dim_var.standard_name
            for idx, allowed_std_names in enumerate(
                [
                    self.time_axis_std_names,
                    self.z_axis_std_names,
                    self.y_axis_std_names,
                    self.x_axis_std_names,
                ]
            ):
                if std_name in allowed_std_names:
                    return self.dimensions_order[idx + 1]
        except AttributeError:
            pass
        try:
            unit = Units(dim_var.units)
            if unit.isreftime or unit.istime:
                return self.dimensions_order[1]
            try:
                if (
                    unit.ispressure
                    or dim_var.units in self.z_axis_units
                    or dim_var.positive.lower() in CFREF().z_axis_orientations
                ):
                    return self.dimensions_order[2]
            except AttributeError:
                pass
            if unit.islongitude:
                return self.dimensions_order[3]
            if unit.islatitude:
                return self.dimensions_order[4]
        except AttributeError:
            pass
        # Fall back to "*" (which means everything else)
        return self.dimensions_order[0]

    @staticmethod
    def is_cf_boundary_variable(nc_var):
        return "bounds" in nc_var.ncattrs()
    
    @staticmethod
    def is_cf_label_variable(nc_var):
        return np.issubdtype(nc_var.dtype, np.str_)

    @staticmethod
    def is_cf_climatology_variable(nc_var):
        return "climatology" in nc_var.ncattrs()

    @staticmethod
    def is_cf_grid_mapping_variable(nc_var):
        return "grid_mapping" in nc_var.ncattrs()

    @staticmethod
    def is_cf_coordinate_variable(nc_var):
        return nc_var.ndim == 1 and nc_var.name == nc_var.dimensions[0]

    @staticmethod
    def is_cf_auxilliary_coordinate_variable(nc_var, all_variables):
        """A netCDF variable is a auxiliary coord var if it is present in
        the `coordinates` attribute of at least one variable of the netCDF data set
        """
        return any(nc_var.name in getattr(v, "coordinates", "") for v in all_variables)

    @lru_cache()
    def cf_standard_name_def(self, std_name):
        for elt in self.__std_names_tree.iter("entry"):
            if elt.attrib["id"] == std_name:
                return {
                    "units": elt.findtext("canonical_units"),
                    "grib": elt.findtext("grib"),
                    "amip": elt.findtext("amip"),
                    "description": elt.findtext("description"),
                }
        raise UnknownStandardNameError(std_name)

# Test 1.
@register(CONVENTION, "cf_filename_extension")
def cf_filename_extension_check(
    ds: Dataset, 
    _, 
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info("Check the filename extension")

    actual = Path(ds.filepath())
    if actual.suffix != ".nc":
        outcome = {
            "status": 1,
            "warnings": [
                f"Non compliant filename extension: '{actual.suffix}'. Should be '.nc'"
            ],
        }
        if verbose: 
            logging.error(
                f"Non compliant filename extension "
                f"suffix {str(actual.suffix):<10} {' '*89} --> NOK"
            )
    else:
        outcome = {
            "status": 1, 
            "info": [f"OK, compliant filename extension '{actual.suffix}'"]
            }
        if verbose: 
            logging.info(
                f"Compliant filename extension: '{str(actual.suffix):<3}' "
                f"{' '*104} --> OK"
            )
    return outcome

# Test 2.
@register(CONVENTION, "cf_convention")
def cf_convention_check(
    ds: Dataset, _, 
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info("Check the CF convention of the Dataset.")
    actual = ds.Conventions
    if CONVENTION not in actual:
        outcome = {
            "status": 0,
            "errors": [
                f"Current Convention metadata ('{actual}' is not compliant with "
                f"expected Convention: '{CONVENTION}'. See CF reference chapter 2.6.1"
            ],
        }
        if verbose:
            logging.error(
                f"Current Convention metadata {str(actual):<15} "
                f"is not compliant "
                f"with expected Convention: {CONVENTION:<15}. "
                f"See CF reference chapter 2.6.1 {' '*5} --> NOK")
    else:
        outcome = {
            "status": 1, 
            "info": [f"OK, Compliant Convention ('{actual}')"]
            }
        if verbose:
            logging.info(f"Compliant CF Convention: {str(actual):<15} {' '*99} --> OK")
    return {"status": 1, "info": ["OK"]}

# Test 3.
@register(CONVENTION, "cf_data_types")
def cf_datatypes_check(
    ds: Dataset, _, 
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info("Check the datatypes of the Dataset.")
    outcome = {"status": 1}
    for var_name, nc_var in ds.variables.items():
        actual = nc_var.dtype
        if actual not in CFREF().data_types:
            outcome.setdefault("errors", []).append(
                f"{var_name} has invalid data type '{actual}"
            )
            outcome["status"] = outcome["status"] and 0
            if verbose:
                logging.error(
                    f"Variable:  {str(var_name):<20} has invalid "
                    f"data type {str(actual):<20} {' '*65} --> NOK")
            status_flag = False
        else:
            outcome.setdefault("info", []).append(f"{var_name} datatype OK")
            if verbose:
                logging.info(
                    f"Variable:  {str(var_name):<20} has correct data "
                    f"type {str(actual):<10} {' '*75} --> OK")  
    return outcome

# Test 4.
@register(CONVENTION, "cf_dimensions_order")
def cf_dimensions_order_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check the order of Dimensions.")
    outcome = {"status": 1}
    for var_name, variable in ds.variables.items():
        dims = variable.dimensions
        if len(dims) > 1:
            # Check dimensions order only for coordinate variables (i.e, dimensions that
            # are also considered to be variables with themselves as the sole dimension)
            try:
                dim_vars = [ds.variables[dim] for dim in dims]
            except KeyError:
                if verbose:
                    logging.info(
                        f"Variable: {str(var_name):<20} One of the dimensions "
                        f"{str(dims)} is not a Coordinate. Continue ..."
                        )
                # One of the dimensions is not a Coordinate (see comment above)
                continue
            dims_order = ("*",) + tuple(
                CFREF().identify_dimension_type(dim) for dim in dim_vars
            )
            if dims_order not in powerset(CFREF().dimensions_order):
                outcome.setdefault("warnings", []).append(
                    f"'{var_name}' dimensions does not follow recommended order "
                    f"{CFREF().dimensions_order}. Found '{dims_order}' instead"
                )
                if verbose:
                    logging.warning(
                        f"Variable:  {str(var_name):<20} dimensions does not "
                        f"follow recommended order, {str(CFREF().dimensions_order):<10}. "
                        f"Found {str(dims_order):<25} instead {' '*10} --> NOK")
            else:
                outcome.setdefault("info", []).append(f"'{var_name}' dimensions order OK")
                if verbose:
                    logging.info(
                        f"Variable:  {str(var_name):<20} dimensions follow recommended order "
                        f"-> {str(dims_order):<25} {' '*43} --> OK")
    return outcome


# Test 5.
@register(CONVENTION, "cf_dimensions_unicity")
def cf_dimensions_unicity_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check the unicity of Dimensions.")
    outcome = {"status": 1}
    for var_name, variable in ds.variables.items():
        dims = variable.dimensions
        dims_count = [dims.count(dim) for dim in dims]
        if any(c > 1 for c in dims_count):
            outcome.setdefault("errors", []).append(
                f"'{var_name}' has duplicate dimensions: {dims}"
            )
            outcome["status"] = 0
            if verbose:
                logging.error(
                    f"Variable:  {str(var_name):<20} with dimensions: "
                    f"{str(dims):<40} (duplicate dimension(s)) {' '*25} -->  NOK")
        else:
            if verbose:
                logging.info(f"Variable:  {str(var_name):<20} with dimensions: "
                    f"{str(dims):<40} {' '*50} --> OK")
            outcome.setdefault("info", []).append(f"'{var_name}' dimension OK")
    return outcome

# Test 6.
@register(CONVENTION, "cf_global_attributes")
def cf_global_attributes_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check the Global Attributes.")
    outcome = {"status": 1}
    status_flag = True
    global_attrs = set(ds.ncattrs())
    recommended = set(CFREF().global_attrs)
    intersect = global_attrs.intersection(recommended)
    missing = recommended - intersect
    if missing:
        outcome.setdefault("warnings", []).append(
            f"Some recommended global attributes are missing: {list(missing)}"
        )
        if verbose:
            logging.warning(
                f"Some recommended global attributes are missing: {list(missing)}"
                )
    else:
        if verbose:
            logging.info("No recommended global attribute is missing")
        outcome.setdefault("info", []).append(
            "No recommended global attribute is missing"
            )
    for attr in global_attrs:
        attr_value = ds.getncattr(attr)
        if verbose:
            logging.info(
                f"Global attributes:  {str(attr):<25} with "
                f"type: {str(type(attr_value)):<30} {' '*52} --> OK")
        if not isinstance(attr_value, str):
            outcome.setdefault("errors", []).append(
                f"Global attributes  '{attr}' is not a string. Found type "
                f"'{type(attr_value)}' instead"
            )
            if verbose:
                logging.error(
                    f"Global attributes:  {str(attr):<25} with type: "
                    f"{str(type(attr_value)):<30} (type is not a string) {' '*29} --> NOK"
                    )
            outcome["status"] = 0
            status_flag = False
    if status_flag:
        outcome.setdefault("info", []).append(
            "All global attribute with correct datatype"
            )
        if verbose:
            logging.info("All global attribute with correct datatype")
    return outcome

# Test 7.
@register(CONVENTION, "cf_missing_data")
def cf_missing_data_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check the missing data.")
    outcome = {"status": 1}
    for var_name, nc_var in ds.variables.items():
        attrs = nc_var.ncattrs()
        if "valid_range" in attrs and any(
            a in attrs for a in ["valid_min", "valid_max"]
        ):
            outcome["status"] = 0
            outcome.setdefault("errors", []).append(
                f"Attributes 'valid_range' must not be defined at the same time as "
                f"either 'valid_min' or 'valid_max' for variable '{var_name}'"
            )
            if verbose:
                logging.error(
                    f"Attributes 'valid_range' must not be defined at the "
                    f"same time as either 'valid_min' or 'valid_max' "
                    f"for variable {str(var_name):<20} {' '*7} --> NOK"
                    )
        else:
            if "valid_range" in attrs:
                _, vmax = nc_var.getncattr("valid_range")
            elif "valid_max" in attrs:
                vmax = nc_var.getncattr("valid_max")
            else:
                vmax = None
            if verbose:
                logging.info(
                    f"Variable:  {str(var_name):<20} "
                    f"with max value: {str(vmax):<20} {' '*71} --> OK"
                    )
                    
            if vmax is not None:
                vmax = np.array(vmax, dtype=nc_var.dtype)
                if "_FillValue" in attrs:
                    fill_value = nc_var._FillValue
                    if fill_value <= vmax:
                        outcome["status"] = 0
                        outcome.setdefault("errors", []).append(
                            f"Fill value '{fill_value}' is lower than valid max "
                            f"'{vmax}' for variable '{var_name}'"
                        )
                        if verbose:
                            logging.error(
                                f"Variable:  {str(var_name):<20} _FillValue {str(fill_value):<10} "
                                f"is lower than valid max {str(vmax):<10} {' '*51} --> NOK")
        if "_FillValue" in attrs:
            fvalue_type = nc_var._FillValue.dtype
            if nc_var.dtype != fvalue_type:
                outcome.setdefault("warnings", []).append(
                    f"Variable '{var_name}' type ({nc_var.dtype}) differs from fill "
                    f"value type ({fvalue_type})"
                )
                logging.warning(
                    f"Variable:  {str(var_name):<20} with type {str(nc_var.dtype):<10} differs "
                    f"from fill value type {str(fvalue_type):<10} {' '*47} --> OK"
                    )
            else:
                if verbose:
                    logging.info(
                        f"Variable:  {str(var_name):<20} with type {str(nc_var.dtype):<10}, "
                        f"fill value with type: {str(fvalue_type):<10} {' '*53} --> OK"
                        )
                outcome.setdefault("info", []).append(
                        f"Variable '{var_name}' with correct fill value type ({fvalue_type})"
                        )
        else:
             if verbose:
                logging.info(
                    f"Variable:  {str(var_name):<20} with type: {str(nc_var.dtype):<10} "
                    f"without _FillValue {' '*67} --> OK"
                    )
    return outcome

#Test 8.
################
@register(CONVENTION, "cf_attributes_values_type")
def cf_attributes_values_type_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check the attributes values.")
    status = 1
    outcome = {"status": status}
    for var_name, nc_var in ds.variables.items():
        attrs = nc_var.ncattrs()
        #print(attrs)
        for attr in attrs:
            attribute_value = nc_var.getncattr(attr)
            #print(f"Variable: {var_name}, Attribute: {attr}, value: {attribute_value}, Data Type: {type(attribute_value)}")
            if attr in ['valid_min', 'valid_max', '_FillValue', 'missing_value']:
                if (isinstance(attribute_value, np.float32) or isinstance(attribute_value, np.float64) 
                    or isinstance(attribute_value, np.int32) or isinstance(attribute_value, np.int64)):
                    outcome.setdefault("info", []).append(
                        f"Variable: {str(var_name)} attribute {str(attr)} "
                        f"attribute value: {str(attribute_value)} "
                        f"type: {str(type(attribute_value))} OK"
                        )
                    if verbose:
                        logging.info(
                            f"Variable:  {str(var_name):<15} attribute {str(attr):<20} "
                            f"type of attributes's value: {str(type(attribute_value)):<25} "
                            f"{' '*28} --> OK"
                        )
                
                else:
                    status = 0
                    outcome.setdefault("errors", []).append(
                        f"Variable: {str(var_name)} attribute {str(attr)} "
                        f"attribute value: {str(attribute_value)} "
                        f"type: {str(type(attribute_value))} wrong attribute value type NOK"
                        )
                    if verbose:
                        logging.info(
                            f"Variable:  {str(var_name):<15} attribute {str(attr):<20} "
                            f"type of attributes's value: {str(type(attribute_value)):<25} " 
                            f"(expected type: 'numeric') {' '*1} --> NOK "
                        )
            else:
                if isinstance(attribute_value, str) or isinstance(attribute_value, str):
                    outcome.setdefault("info", []).append(
                        f"Variable '{var_name}' with correct attributes value type ({type(attribute_value)})"
                        )
                    if verbose:
                        logging.info(
                            f"Variable:  {str(var_name):<15} attribute {str(attr):<20} "
                            f"type of attributes's value: {str(type(attribute_value)):<25} "
                            f"{' '*28} --> OK"
                        )
                else:
                    status = 0
                    outcome.setdefault("errors", []).append(
                        f"Variable: {str(var_name)} attribute {str(attr)} "
                        f"attribute value: {str(attribute_value)} "
                        f"type: {str(type(attribute_value))} wrong attribute value type NOK"
                        )
                    if verbose:
                        logging.info(
                            f"Variable:  {str(var_name):<15} attribute {str(attr):<20} "
                            f"type of attributes's value: {str(type(attribute_value)):<25} "
                            f"(expected type: 'string') {' '*1} --> NOK "
                        )
    
    outcome["status"] = status
    return outcome



################

# Test 9.
@register(CONVENTION, "cf_naming_convention")
def cf_naming_convention_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check the naming convention.")
    outcome = {"status": 1}
    naming_convention = re.compile("[a-zA-Z][a-zA-Z0-9_]*")

    def _check(name, err_msg):
        status_flag = True
        if not naming_convention.match(name):
            outcome["status"] = 0
            outcome.setdefault("errors", []).append(err_msg)
            if verbose:
                logging.error(
                    f"{str(name):<25} doesn't follows the name convention {' '*78} --> NOK"
                    )
                logging.error(f"{err_msg}")
            status_flag = False
        else:
            if verbose:
                logging.info(
                    f"{str(name):<25} follows the name convention {' '*86} --> OK"
                    )
        return status_flag


    for var_name, nc_var in ds.variables.items():
        if verbose:
            logging.info(f"{str('Variable'):<18}    --> {var_name}")
        variable_convention = _check(
            var_name,
            (
                f"Variable name '{var_name}' does not follow naming "
                f"convention '{naming_convention.pattern}'"
            ),
        )
        for attribute in nc_var.ncattrs():
            # Make an exception for _FillValue. CF convention is not clear about this:
            # it says attributes shouldn't start with an underscore, but then there is
            # this one it talks about in the chapter on Missing Values
            if attribute != "_FillValue":
                attribute_convention = _check(
                    attribute,
                    (
                        f"Attribute '{attribute}' of variable '{var_name}' does not "
                        f"follow naming convention '{naming_convention.pattern}'"
                    ),
                )
                if not attribute_convention:
                    overall_status_flag = False

    if verbose:
        logging.info(f"Global attributes  ")
    for global_attribute in ds.ncattrs():
        if global_attribute != "_FillValue":
            global_attribute_convention = _check(
                global_attribute,
                (
                    f"Global attribute '{global_attribute}' does not follow naming "
                    f"convention '{naming_convention.pattern}'"
                ),
            )
    if global_attribute_convention:
        outcome.setdefault("info", []).append(
            f"Name convention is correct for all the variables and attributes."
            )
    else:
        outcome.setdefault("error", []).append(f"Name convention failed ")
            
    return outcome


# Test 10.
@register(CONVENTION, "cf_naming_unicity")
def cf_naming_unicity_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check the naming unicity.")
    outcome = {"status": 1}
    ds_names = Counter(k.lower() for k in ds.variables)
    for name, count in ds_names.items():
        if count > 1:
            outcome["status"] = 0
            err_msg = (f"Variable '{name}' is not unique. "
                f"Found {count} occurrences in the dataset")
            outcome.setdefault("errors", []).append(err_msg)
            if verbose:
                logging.error(
                    f"Variable:  {str(name):<20} is not unique. "
                    f"Found {str(count):2} occurrences in the dataset "
                    f"{' '*57} --> NOK"
                )
        else:
            info_msg = (
                f"Variable: {name}  {count} "
                f"occurrence in the dataset OK"
            )
            if verbose:
                logging.info(
                    f"Variable:  {str(name):<20} unique {str(count):<2} "
                    f"occurrence in the dataset {' '*72} --> OK"
                )
            outcome.setdefault("info", []).append(f"'{name}' is unique")
    return outcome


# Test 11.
@register(CONVENTION, "cf_ancillary_data")
def cf_ancillary_data_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check ancillary data.")
    outcome = {"status": 1}    
    variables = set(ds.variables.keys())
    for var_name, nc_var in ds.variables.items():
        try:
            anc_vars = nc_var.getncattr("ancillary_variables")
            if not isinstance(anc_vars, str):
                outcome["status"] = 0
                outcome.setdefault("errors", []).append(
                    f"Variable '{var_name}' attribute 'ancillary_variables' must "
                    f"be a string"
                )
                logging.error(
                    f"Variable:  {str(var_name):<20} attribute 'ancillary_variables' "
                    f"must be a string {' '*59} -->  NOK"
                    )
            else:
                for anc_var in anc_vars.split():
                    if anc_var not in variables:
                        outcome["status"] = 0
                        outcome.setdefault("errors", []).append(
                            f"Variable '{anc_var}' is declared as Ancillary Variable "
                            f"for '{var_name}' but is not defined in the dataset"
                        )
                logging.error(
                    f"Variable:  {str(anc_var):<20} is declared as Ancillary "
                    f"variable for {str(var_name):<20} but is not defined in "
                    f"the dataset {' '*15} -->  NOK"
                    )
        except AttributeError:
            #pass
            if verbose:
                logging.info(
                    f"Variable:  {str(var_name):<20} is not declared as Ancillary "
                    f"Variable {' '*70} --> OK"
                    )
            outcome.setdefault("info", []).append(f"'{var_name}' not ancillary")
            
    return outcome



# Test 12.
@register(CONVENTION, "cf_standard_names")
def cf_standard_names_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check standard names.")
    outcome = {"status": 1}
    for var_name, nc_var in ds.variables.items():
        attrs = nc_var.ncattrs()
        status_flag = True
        if (
            all(attr not in attrs for attr in ["standard_name", "long_name"])
            and not CFREF.is_cf_boundary_variable(nc_var)
            and not CFREF.is_cf_label_variable(nc_var)
        ):
            if "bnds" in var_name:
                continue
            warning_msg = (
                f"Variable: {str(var_name):<15} description with 'long_name' and 'standard_name' "
                f"attributes is highly recommended. Not found"
            )
            outcome.setdefault("warnings", []).append(warning_msg)
            if verbose:
                logging.warning(
                        f"Variable:  {str(var_name):<15} description with 'long_name' "
                        f"and 'standard_name' attributes is highly recommended. Not found. "
                    )
                if "C3S" in ds.Conventions and "hcrs" in var_name:
                    logging.info(
                        f"Variable:  {str(var_name):<15} without 'long_name' and "
                        "'standard_name'. It's allowed in C3S "
                        f"conventions {' '*40} --> OK"
                        )
                else:
                    logging.warning(warning_msg)
        else:
            if verbose:
                logging.info(
                    f"Variable:  {str(var_name):<15} is described with 'long_name' "
                    f"and 'standard_name' {' '*63} --> OK"
                    )
        try:
            std_name, modifier = __get_std_name(nc_var.getncattr("standard_name"))
            if not isinstance(std_name, str):
                error_msg = (
                    f"Attribute 'standard_name' of variable '{var_name}' must be a "
                    f"string. Currently '{type(std_name)}'"
                )
                outcome.setdefault("errors", []).append(error_msg)
                if verbose:
                    logging.error(
                        f"Variable:  {str(var_name):<15} attribute 'standard_name' must be a "
                        f"string. Currently {type(std_name):<20} {' '*39} --> NOK"
                    )
                status_flag = False
            else:
                if std_name is None and modifier is None:
                    outcome["status"] = 0
                    error_msg = (
                        f"Only two blank separated names allowed for attribute "
                        f"'standard_name' of variable '{var_name}'. Currently "
                        f"{len(nc_var.getncattr('standard_name').split())}"
                    )
                    outcome.setdefault("errors", []).append(error_msg)
                    if verbose:
                        logging.error(
                            f"Variable:  {str(var_name):<15} only two blank separated "
                            f"names allowed for attribute 'standard_name', currently "
                            f"{str(len(nc_var.getncattr('standard_name').split())):<3} "
                            f"{' '*29} --> NOK"
                        )
                    status_flag = False
                else:
                    _ = CFREF().cf_standard_name_def(std_name)
                    if (
                        modifier is not None
                        and modifier not in CFREF().cf_units_modifiers
                    ):
                        outcome["status"] = 0
                        error_msg = (
                            f"Standard name modifier for variable '{var_name}' "
                            f"({modifier}) is not a recognized CF standard name "
                            f"modifier"
                        )
                        outcome.setdefault("errors", []).append(error_msg)
                        logging.error(
                            f"Variable:  {str(var_name):<15} standard name modifier "
                            f"{str(modifier):<20} is not a recognized CF standard name "
                            f"modifier {' '*23} --> NOK"
                        )
                        status_flag = False
        except AttributeError:
            pass
        except UnknownStandardNameError:
            outcome.setdefault("errors", []).append(
                f"Attribute 'standard_name' of variable '{var_name}' ({std_name}) "
                f"is not a recognized CF standard name"
            )
            if verbose:
                logging.error(
                    f"Variable:  {str(var_name):<15} attribute 'standard_name' {str(std_name):<49} "
                    f"is not a recognized CF standard name {' '*1} --> NOK"
                )
        if status_flag:
            if verbose:
                logging.info(
                    f"Variable:  {str(var_name):<15} "
                    f"standard name is checked successfully {' '*75} --> OK ")
            outcome.setdefault("info", []).append(f"'{var_name}' standard name OK")
    return outcome


# Test 13. Check the units of the variables
@register(CONVENTION, "cf_units")
def cf_units_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check the units of the variables.")
    outcome = {"status": 1}
    institute_id = ds.institute_id
    system = ds.source.split()[0].split(":")[0]
    
    for var_name, nc_var in ds.variables.items():
        attrs = nc_var.ncattrs()
        status_flag = True
        if all(
            not condition
            for condition in [
                CFREF.is_cf_label_variable(nc_var),
                CFREF.is_cf_boundary_variable(nc_var),
                CFREF.is_cf_climatology_variable(nc_var),
                CFREF.is_cf_grid_mapping_variable(nc_var),
                set(attrs).intersection({"flag_meanings", "flag_marks", "flag_values"}),
            ]
        ):
            if "units" in attrs:
                units_attr = nc_var.getncattr("units")
                if not isinstance(units_attr, str):
                    outcome["status"] = 0
                    status_flag = False
                    error_msg = (
                        f"Attribute 'units' of variable '{var_name}' must be a string "
                        f"(currently '{type(units_attr)}'"
                    )
                    outcome.setdefault("errors", []).append(error_msg)
                    if verbose:
                        logging.error(
                            f"Variable:  {str(var_name):<15} attribute 'units' must be a string, "
                            f"currently {str(type(units_attr)):<20} {' '*46} --> NOK"
                        )
                elif units_attr in CFREF.deprecated_units:
                    warning_message = (
                        f"Value of attribute 'units' of variable '{var_name}' is "
                        f"deprecated: '{units_attr}'. No further checks done."
                    )
                    outcome.setdefault("warnings", []).append(warning_message)
                    if verbose:
                        logging.warning(
                            f"Variable:  {str(var_name):<15} value of attribute 'units' is "
                            f"deprecated: {str(units_attr):<20}. No further checks done {' '*26} --> OK"
                        )
                else:
                    units = Units(units_attr)
                    if not units.isvalid:
                        outcome["status"] = 0
                        status_flag = False
                        outcome.setdefault("errors", []).append(
                            f"Value of attribute 'units' of variable '{var_name}' is "
                            f"invalid: '{units}'"
                        )
                        if verbose:
                            logging.error(
                                f"Variable:  {str(var_name):<15} value of attribute 'units' "
                                f"is invalid: {str(units):20} {' '*52} --> NOK"
                                )
                    elif "standard_name" in attrs:
                        std_name, modifier = __get_std_name(
                            nc_var.getncattr("standard_name")
                        )
                        if std_name is None:
                            outcome.setdefault("errors", []).append(
                                "Further units checking skipped due to invalid "
                                "standard name"
                            )
                            if verbose:
                                logging.error(
                                    f"Variable:  {str(var_name):<15} further units checking skipped due to invalid "
                                    f"standard name {' '*53} --> NOK"
                                    )
                        else:
                            known_units = Units(
                                CFREF().cf_standard_name_def(std_name)["units"]
                            )
                            if not known_units.isvalid:
                                status_flag = False
                                outcome["status"] = 0
                                outcome.setdefault("errors", []).append(
                                    f"Units of variable '{var_name}' ('{units}') "
                                    f"cannot be compared with standard name canonical "
                                    f"units because the canonical units is invalid "
                                    f"('{known_units}')"
                                )
                                if verbose:
                                    logging.error(
                                    f"Variable:  {str(var_name):<15} units {str(units):20} "
                                    f"cannot be compared with standard name canonical "
                                    f"units, the canonical units is invalid "
                                    f"--> NOK"
                                )
                            else:
                                known_units = Units(
                                    CFREF.cf_units_modifiers.get(modifier, known_units)
                                )
                                if units.isreftime:
                                    units = Units(units_attr.split()[0])
                                if not units.equivalent(known_units):
                                    exceptions = excep.get("exceptions", {}).get(
                                        institute_id, {}).get(system, {}).get(
                                            "units_per_variable", {}).get(var_name, {}
                                            )
                                    if units_attr in exceptions:
                                        outcome["status"] = 1
                                        outcome.setdefault("warnings", []).append(
                                            f"Units of variable '{var_name}' ('{units}') "
                                            f"is not consistent with standard name "
                                            f"canonical units ('{known_units}'). "
                                            f"Under exception."
                                        )
                                        if verbose:
                                            logging.warning(
                                                f"Variable:  {str(var_name):<15} "
                                                f"units {str(units):15} are not consistent "
                                                f"with standard name canonical units "
                                                f"{str(known_units):<15} (under exception) {' '*3} --> OK"
                                        )
                                    else:
                                        if var_name == 'temperature':
                                            pass                                        
                                        else:
                                            outcome["status"] = 0
                                            status_flag = False
                                            outcome.setdefault("errors", []).append(
                                                f"Units of variable '{var_name}' ('{units}') "
                                                f"is not consistent with standard name "
                                                f"canonical units ('{known_units}')"
                                                )
                                            if verbose:
                                                logging.error(
                                                f"Variable:  {str(var_name):<15} units {str(units):<20} "
                                                f"is not consistent with standard name "
                                                f"canonical units {str(known_units):<20} {' '*12} --> NOK"
                                            )
                if status_flag:
                    outcome.setdefault("info", []).append(f"'{var_name}' units OK")
                    if verbose:
                        logging.info(
                            f"Variable:  {str(var_name):<15} with correct "
                            f"units: {str(units_attr):<54} {' '*38} --> OK")
            else:
                outcome.setdefault("info", []).append(
                    f"'{var_name}' without units"
                    )
                if verbose:
                    logging.info(
                        f"Variable:  {str(var_name):<15} without "
                        f"units {' '*99} --> OK"
                        ) 
    return outcome


# Test 14. Check flags
@register(CONVENTION, "cf_flags")
def cf_flags_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check flags.")
    outcome = {"status": 1}
    flag_meanings_pattern = re.compile("^[0-9A-Za-z_\-@+.]+$")
    for var_name, nc_var in ds.variables.items():
        status_flag = True
        attrs = nc_var.ncattrs()
        if "standard_name" in attrs:
            std_name, modifier = __get_std_name(nc_var.getncattr("standard_name"))
            if std_name is None:
                warning_message = (
                    "Further flags checking skipped due to invalid standard name"
                )
                outcome.setdefault("errors", []).append(warning_message)
                if verbose:
                    logging.error(
                        f"Variable:  {str(var_name):<15} Further flags checking "
                        f"skipped due to invalid standard name {' '*53} --> NOK"
                    )
            else:
                if (
                    modifier in (m for m in CFREF().cf_units_modifiers if "flag" in m)
                    and "flag_meanings" not in attrs
                ):
                    outcome["status"] = 0
                    status_flag = False
                    error_message = (
                        f"Standard name modified to a flag but no 'flag_meanings' "
                        f"found in attributes for variable '{var_name}'"
                    )
                    outcome.setdefault("errors", []).append(error_message)
                    if verbose:
                        logging.error(
                            f"Variable:  {str(var_name):<15} standard name modified to a flag but no 'flag_meanings' "
                            f"found in attributes {' '*37} --> NOK"
                        )
        if "flag_meanings" in attrs and all(
            a not in attrs for a in ["flag_values", "flag_masks"]
        ):
            outcome["status"] = 0
            status_flag = False
            error_message = (
                f"Attribute 'flag_meanings' is defined for variable '{var_name}' but "
                f"neither 'flag_values' nor 'flag_masks' are defined"
            )
            outcome.setdefault("errors", []).append(error_message)
            if verbose:
                logging.error(
                    f"Variable:  {str(var_name):<15} attribute 'flag_meanings' is defined but "
                    f"neither 'flag_values' nor 'flag_masks' are defined {' '*21} --> NOK"
                )
        elif "flag_meanings" not in attrs and any(
            a in attrs for a in ["flag_values", "flag_masks"]
        ):
            outcome["status"] = 0
            status_flag = False
            error_message = (
                f"Attribute 'flag_meanings' is missing for variable '{var_name}' "
                f"although either 'flag_values' or 'flag_masks' attributes are defined"
            )
            outcome.setdefault("errors", []).append(error_message)
            if verbose:
                logging.error(
                    f"Variable:  {str(var_name):<15} attribute 'flag_meanings' is missing "
                    f"although either 'flag_values' or 'flag_masks' "
                    f"attributes are defined {' '*7} --> NOK"
                )
        elif "flag_meanings" in attrs:
            flag_meanings = nc_var.getncattr("flag_meanings")
            if not isinstance(flag_meanings, str):
                outcome["status"] = 0
                status_flag = False
                error_message = (
                    f"Value of attribute '{flag_meanings}' must be a string. Found "
                    f"'{type(flag_meanings)}' instead"
                )
                outcome.setdefault("errors", []).append(error_message)
                if verbose:
                    logging.error(
                        f"Variable:  {str(var_name):<15} value of attribute {str(flag_meanings):<20} "
                        f"must be a string. Found "
                        f"{(type(flag_meanings)):<20} instead {' '*20} --> NOK"
                    )
            elif not all(
                flag_meanings_pattern.match(item) for item in flag_meanings.split()
            ):
                outcome["status"] = 0
                status_flag = False
                error_message = (
                    f"Incorrect Syntax for flag_meanings attribute value of "
                    f"variable '{var_name}': '{flag_meanings}'. Must be: "
                    f"'{flag_meanings_pattern}'"
                )
                outcome.setdefault("errors", []).append(error_message)
                if verbose:
                    logging.error(
                        f"Variable:  {str(var_name):<15} incorrect Syntax for "
                        f"flag_meanings attribute value: {str(flag_meanings):<20} Must be: "
                        f"{str(flag_meanings_pattern):<20} {' '*10} --> NOK"
                    )
            if "flag_values" in attrs:
                flag_values = np.array(nc_var.getncattr("flag_values"))
                if not np.issubdtype(flag_values.dtype, nc_var.dtype):
                    outcome["status"] = 0
                    status_flag = False
                    error_message = (
                        f"Values of attribute for 'flag_values' must have the same type "
                        f"as variable '{var_name}'. Found '{flag_values.dtype}' instead"
                    )
                    outcome.setdefault("errors", []).append(error_message)
                    if verbose:
                        logging.error(
                            f"Variable:  {str(var_name):<15} values of attribute for 'flag_values' must have the same type "
                            f"as the variable. Found {str(flag_values.dtype):<20} {' '*8} --> NOK"
                        )
                elif len(flag_values) != len(flag_meanings):
                    outcome["status"] = 0
                    status_flag = False
                    error_message = (
                        f"Attribute 'flag_values' of variable '{var_name}' must have "
                        f"the same number of elements as attribute 'flag_meanings'"
                    )
                    outcome.setdefault("errors", []).append(error_message)
                    if verbose:
                        logging.error(
                            f"Variable:  {str(var_name):<15} attribute 'flag_values' must have "
                            f"the same number of elements as attribute 'flag_meanings' {' '*22} --> NOK"
                        )

                elif len(flag_values) != len(set(flag_values)):
                    outcome["status"] = 0
                    status_flag = False
                    error_message = (
                        f"Values for attribute 'flag_values' of variable '{var_name}' "
                        f"must be unique"
                    )
                    outcome.setdefault("errors", []).append(error_message)
                    if verbose:
                        logging.error(
                            f"Variable:  {str(var_name):<15} values for attribute 'flag_values' "
                            f"must be unique {' '*63} --> NOK"
                        )
            if "flag_masks" in attrs:
                flag_masks = np.array(nc_var.getncattr("flag_masks"))
                if not np.issubdtype(flag_masks.dtype, nc_var.dtype):
                    status_flag = False
                    outcome["status"] = 0
                    error_message = (
                        f"Values of attribute 'flag_masks' must have the same type "
                        f"as variable '{var_name}'. Found '{flag_masks.dtype}' instead"
                    )
                    outcome.setdefault("errors", []).append(error_message)
                    if verbose:
                        logging.error(
                            f"Variable:  {str(var_name):<15} values of attribute 'flag_masks' must have the same type "
                            f"as the variable. Found {str(flag_masks.dtype):<20} {' '*12} --> NOK"
                        )
                elif nc_var.dtype not in [
                    np.char,
                    np.dtype("b"),
                    np.dtype("i4"),
                    np.int,
                ]:
                    expected = "or ".join(
                        str(v) for v in [np.char, np.dtype("b"), np.dtype("i4"), np.int]
                    )
                    outcome["status"] = 0
                    status_flag = False
                    error_message = (
                        f"Variable '{var_name}' type is not appropriate for flag "
                        f"masking ('{nc_var.dtype}'). Must be one of {expected}"
                    )
                    outcome.setdefault("errors", []).append(error_message)
                    if verbose:
                        logging.error(
                            f"Variable:  {str(var_name):<15} type is not appropriate for flag "
                            f"masking {str(nc_var.dtype):<20}. Must be one of {str(expected):<20} "
                            f"{' '*34} --> NOK"
                        )
                elif len(flag_masks) != len(flag_meanings):
                    outcome["status"] = 0
                    status_flag = False
                    error_message = (
                        f"Attribute 'flag_masks' of variable '{var_name}' must have "
                        f"the same number of elements as attribute 'flag_meanings'"
                    )
                    outcome.setdefault("errors", []).append(error_message)
                    if verbose:
                        logging.error(
                            f"Variable:  {str(var_name):<15} attribute 'flag_masks' must have "
                            f"the same number of elements as attribute 'flag_meanings' {' '*23} --> NOK"
                        )
                elif np.count_nonzero(flag_masks) != flag_masks.size:
                    outcome["status"] = 0
                    status_flag = False
                    error_message = (
                        f"Attribute 'flag_masks' of variable '{var_name}' must have "
                        f"only non zero elements in its values. Currently "
                        f"{np.count_nonzero(flag_masks)} zero values"
                    )
                    outcome.setdefault("errors", []).append(error_message)
                    if verbose:
                        logging.error(
                            f"Variable:  {str(var_name):<15} attribute 'flag_masks' must have "
                            f"only non zero elements in its values. Currently "
                            f"{str(np.count_nonzero(flag_masks)):<17} zero values {' '*2} --> NOK"
                        )
                elif "flag_values" in attrs:
                    flag_values = np.array(nc_var.getncattr("flag_values"))
                    for mask in flag_masks:
                        if np.count_nonzero((nc_var[:] & mask) == flag_values) == 0:
                            outcome["status"] = 0
                            status_flag = False
                            error_message = (
                                f"Bitwise AND of flag_masks value '{mask}' and "
                                f"'{var_name}' values results in a value not "
                                f"available in attribute 'flag_values'. Must result"
                                f" in '{flag_values}'"
                            )
                            outcome.setdefault("errors", []).append(error_message)
                            if verbose:
                                logging.error(
                                    f"Variable:  {str(var_name):<15} Bitwise AND of flag_masks value '{mask}' and "
                                    f"'{var_name}' values results in a value not "
                                    f"available in attribute 'flag_values'. Must result"
                                    f" in '{flag_values}' --> NOK"
                                )
        if status_flag:
            outcome.setdefault("info", []).append(f"'{var_name}' flags OK")
            if verbose:
                if "flag_meanings" not in attrs:
                    logging.info(
                        f"Variable:  {str(var_name):<15} no 'flag_meaning' "
                        f"attribute {' '*85} --> OK")
                if "flag_values" not in attrs:
                    logging.info(
                        f"Variable:  {str(var_name):<15} no "
                        f"'flag_values' attribute {' '*86} --> OK")
                if "flag_masks" not in attrs:
                    logging.info(
                        f"Variable:  {str(var_name):<15} no "
                        f"'flag_masks' attribute {' '*87} --> OK")

    return outcome


# Test 15. Check coordinates of the variables.
@register(CONVENTION, "cf_coordinates_variables")
def cf_coordinates_variables_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check coordinates of the variables.")
    outcome = {"status": 1}
    nc_variables = ds.variables.values()
    for var_name, nc_var in zip(ds.variables, nc_variables):
        status_flag = True
        if CFREF().is_cf_coordinate_variable(
            nc_var
        ) or CFREF().is_cf_auxilliary_coordinate_variable(nc_var, nc_variables):
            try:
                unit = nc_var.getncattr("units")
            except AttributeError:
                try:
                    std_name = nc_var.getncattr("standard_name")
                    if std_name not in CFREF().dimensionless_vertical_coordinates:
                        outcome["status"] = 0
                        status_flag = False
                        error_message = (
                            f"Coordinate variables must have units or have their "
                            f"standard_name in the list of dimensionless vertical "
                            f"coordinates"
                        )
                        outcome.setdefault("errors", []).append(error_message)
                        if verbose:
                            logging.error(
                                f"Coordinate variables must have units or have their "
                                f"standard_name in the list of dimensionless vertical "
                                f"coordinates {' '*25} --> NOK"
                            )
                except AttributeError:
                    pass
            else:
                try:
                    positive = nc_var.getncattr("positive")
                    if positive.lower() not in CFREF().z_axis_orientations:
                        status_flag = False
                        outcome["status"] = 0
                        error_message = (
                            f"Value of 'positive' attribute ({positive}) is not allowed. "
                            f"Use one of '{CFREF().z_axis_orientations}' instead"
                        )
                        outcome.setdefault("errors", []).append(error_message)
                        if verbose:
                            logging.error(
                                f"Value of 'positive' attribute {str(positive):<10} is not allowed. "
                                f"Use one of {str(CFREF().z_axis_orientations):<10} instead "
                                f"{' '*63} --> NOK"
                            )
                except AttributeError:
                    pass
                dimension_type = CFREF().identify_dimension_type(nc_var)
                axis = getattr(nc_var, "axis", "")
                if dimension_type == "*":
                    if axis == "E" and "C3S" in ds.Conventions:
                        outcome.setdefault("warnings", []).append(
                            f"Axis E of coordinate '{var_name}' is not part of "
                            f"CF-1.6 but it is mandatory in C3S-0.1 "
                            f"(may be allowed in CF higher version)"
                        )
                        if verbose:
                            logging.info(
                                f"Variable:  {str(var_name):<15} axis E of "
                                f"coordinate {str(var_name):<15} is not part of "
                                f"CF-1.6 but it's mandatory in C3S 0.1 {' '*24} --> OK"
                            )
                    elif not axis:
                        outcome.setdefault("warnings", []).append(
                            f"Axis attribute not provided for coordinate variable"
                            f" '{var_name}'"
                        )
                        if verbose:
                            logging.warning(
                                f"Variable:  {str(var_name):<15} axis attribute "
                                f"not provided for coordinate variable '{var_name}'"
                                )
                    else:
                        status_flag = False
                        outcome["status"] = 0
                        outcome.setdefault("errors", []).append(
                            f"Unsupported value of attribute 'axis' for coordinate "
                            f"variable '{var_name}': '{axis}'. Should be one of "
                            f"'{CFREF().dimensions_order[1:] + ('E',)}'"
                        )
                        if verbose:
                            logging.error(
                                f"Variable:  {str(var_name):<15} unsupported value of "
                                f"attribute 'axis' {str(axis):<20} "
                                f"Should be one of "
                                f"{str(CFREF().dimensions_order[1:] + ('E',)):<20} "
                                f"{' '*16} --> NOK"
                            )
                else:
                    # for time coordinates is allowed not to have axis and 
                    # at the same time the units can be != 1 
                    # if axis != dimension_type and unit != "1":
                    if axis != dimension_type and unit != "1" and dimension_type != "T":
                        status_flag = False
                        outcome["status"] = 0
                        outcome.setdefault("errors", []).append(
                            f"Attribute 'axis' (value: '{axis}') of coordinate variable"
                            f" '{var_name}' is not consistent with its unit '{unit}'. "
                            f"It should be set to '{dimension_type}' or the 'unit' "
                            f"should be 1"
                        )
                        if verbose:
                            logging.error(
                                f"Variable:  {str(var_name):<15} Attribute 'axis' "
                                f"(value: '{axis}') of coordinate variable"
                                f" '{var_name}' is not consistent with its unit '{unit}'. "
                                f"It should be set to '{dimension_type}' or the 'unit' "
                                f"should be 1"
                            )
        else:
            axis = getattr(nc_var, "axis", "")
            positive = getattr(nc_var, "positive", "")
            if axis:
                outcome.setdefault("warnings", []).append(
                    f"Value of attribute 'axis' of variable '{var_name}' ('{axis}') "
                    f"may not be allowed because variable is not identified as a "
                    f"coordinate variable"
                )
                if verbose:
                    logging.warning(
                        f"Variable:  {str(var_name):<15} Value of attribute "
                        f"'axis' of variable '{var_name}' ('{axis}') "
                        f"may not be allowed because variable is not identified as a "
                        f"coordinate variable"
                    )
            if positive:
                outcome.setdefault("warnings", []).append(
                    f"Value of attribute 'positive' of variable '{var_name}' "
                    f"('{positive}') may not be allowed because variable is not "
                    f"identified as a coordinate variable"
                )
                if verbose:
                    logging.warning(
                        f"Variable:  {str(var_name):<15} Value of attribute "
                        f"'positive' of variable '{var_name}' "
                        f"('{positive}') may not be allowed because variable is not "
                        f"identified as a coordinate variable"
                    )
        if status_flag:
            outcome.setdefault("info", []).append(f"'{var_name}' axis OK")
            if verbose:
                if axis:
                    logging.info(
                        f"Variable:  {str(var_name):<15} "
                        f"with axis: {str(axis):<10} {' '*91} --> OK")
                else:
                    logging.info(
                        f"Variable:  {str(var_name):<15} without axis {' '*100} --> OK")
    return outcome


# Test 16. Check dimensionless vertical coordinates. 
@register(CONVENTION, "cf_dimensionless_vertical_coordinates")
def cf_dimensionless_vertical_coordinates_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check dimensionless vertical coordinates.")
    outcome = {"status": 1}
    for var_name, nc_var in ds.variables.items():
        try:
            std_name = nc_var.getncattr("standard_name")
            regex = CFREF().dimensionless_vertical_coordinates.get(std_name)
            if not regex:
                outcome.setdefault("info", []).append(
                    f"'{var_name}' no dimensionless vertical coordinates OK"
                    )
                if verbose:
                    logging.info(
                        f"Variable:  {str(var_name):<15} not dimensionless "
                        f"vertical coordinates {' '*74} --> OK")
            if regex and not regex.match(nc_var.getncattr("formula_terms")):
                outcome["status"] = 0
                outcome.setdefault("errors", []).append(
                    f"Value of attribute 'formula_terms' of variable '{var_name}' "
                    f"does not match the known pattern for this standard_name "
                    f"'{std_name}'. Must match: '{regex}' (Python Regex)"
                )
                if verbose:
                    logging.error(
                        f"Variable:  {str(var_name):<15} Value of attribute 'formula_terms' "
                        f"does not match the known pattern for this standard_name "
                        f"'{std_name}'. Must match: '{regex}' (Python Regex)"
                    )
        except AttributeError:
            #pass
            if verbose:
                logging.info(
                    f"Variable:  {str(var_name):<15} without "
                    f"standard name {' '*91} --> OK")
    return outcome


# Test 17. Check latitude coordinate.
@register(CONVENTION, "cf_latitude")
def cf_latitude_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check latitude coordinate.")
    outcome = {"status": 1}
    nc_variables = ds.variables.values()
    for var_name, nc_var in zip(ds.variables, nc_variables):
        if CFREF().is_cf_coordinate_variable(
            nc_var
        ) or CFREF().is_cf_auxilliary_coordinate_variable(nc_var, nc_variables):
            unit = getattr(nc_var, "units", "")
            if unit in CFREF().cf_acceptable_latitude_units + (
                CFREF().cf_recommended_latitude_unit,
            ):
                dim_type = CFREF().identify_dimension_type(nc_var)
                std_name = getattr(nc_var, "standard_name", "")
                axis = getattr(nc_var, "axis", "")
                if any([std_name != "latitude", dim_type != axis != "Y"]):
                    outcome["status"] = 0
                    outcome.setdefault("errors", []).append(
                        f"Variable '{var_name}' is identified as a latitude "
                        f"coordinate variable but has inconsistent standard_name "
                        f"('{std_name}') and/or axis ('{axis}') attributes and/or "
                        f"inconsistent dimension type ('{dim_type}')"
                    )
                    if verbose:
                        logging.error(
                            f"Variable:  {str(var_name):<15} is identified as a latitude "
                            f"coordinate variable but has inconsistent standard_name "
                            f"('{std_name}') and/or axis ('{axis}') attributes and/or "
                            f"inconsistent dimension type ('{dim_type}')"
                        )
                else:
                    outcome.setdefault("info", []).append(
                        f"'{var_name}' latitude coordinate variable OK"
                        )
                    if verbose:
                        logging.info(
                            f"Variable:  {str(var_name):<15} is identified as a latitude "
                            f"coordinate variable {' '*65} --> OK"
                        )
                        logging.info(
                            f"Variable:  {str(var_name):<15} consistent standard_name "
                            f"('{std_name:<8}') attribute {' '*65} --> OK"
                        )
                        logging.info(
                            f"Variable:  {str(var_name):<15} consistent axis "
                            f"('{axis:<1}') attribute {' '*81} --> OK"
                        )
                        logging.info(
                            f"Variable:  {str(var_name):<15} consistent dimension "
                            f"type ('{dim_type:<1}') {' '*81} --> OK"
                        )
            else:
                outcome.setdefault("info", []).append(
                    f"'{var_name}' not latitude coordinate variable"
                    )
                if verbose:
                    logging.info(
                        f"Variable:  {str(var_name):<15} is not latitude "
                        f"coordinate variable"
                        )
        else:
            outcome.setdefault("info", []).append(
                f"'{var_name}' not latitude coordinate variable"
                ) 
            if verbose:
                logging.info(
                    f"Variable:  {str(var_name):<15} is not "
                    f"coordinate variable"
                    )
    return outcome


# Test 18. Check longitude coordinate.
@register(CONVENTION, "cf_longitude")
def cf_longitude_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check longitude coordinate.")
    outcome = {"status": 1}
    nc_variables = ds.variables.values()
    for var_name, nc_var in zip(ds.variables, nc_variables):
        if CFREF().is_cf_coordinate_variable(
            nc_var
        ) or CFREF().is_cf_auxilliary_coordinate_variable(nc_var, nc_variables):
            unit = getattr(nc_var, "units", "")
            if unit in CFREF().cf_acceptable_longitude_units + (
                CFREF().cf_recommended_longitude_unit,
            ):
                dim_type = CFREF().identify_dimension_type(nc_var)
                std_name = getattr(nc_var, "standard_name", "")
                axis = getattr(nc_var, "axis", "")
                if any([std_name != "longitude", dim_type != axis != "X"]):
                    outcome["status"] = 0
                    outcome.setdefault("errors", []).append(
                        f"Variable '{var_name}' is identified as a longitude "
                        f"coordinate variable but has inconsistent standard_name "
                        f"('{std_name}') and/or axis ('{axis}') attributes and/or "
                        f"inconsistent dimension type ('{dim_type}')"
                    )
                    if verbose:
                        logging.error(
                            f"Variable:  {str(var_name):<15} is identified as a longitude "
                            f"coordinate variable but has inconsistent standard_name "
                            f"('{std_name}') and/or axis ('{axis}') attributes and/or "
                            f"inconsistent dimension type ('{dim_type}')"
                        )
                else:
                    outcome.setdefault("info", []).append(
                        f"'{var_name}' longitude coordinate variable OK"
                        )
                    if verbose:
                        logging.info(
                            f"Variable:  {str(var_name):<15} is identified as a longitude "
                            f"coordinate variable {' '*64} --> OK"
                        )
                        logging.info(
                            f"Variable:  {str(var_name):<15} consistent standard_name "
                            f"('{std_name:<9}') attribute {' '*64} --> OK"
                        )
                        logging.info(
                            f"Variable:  {str(var_name):<15} consistent axis "
                            f"('{axis:<1}') attribute {' '*81} --> OK"
                        )
                        logging.info(
                            f"Variable:  {str(var_name):<15} consistent dimension "
                            f"type ('{dim_type:<1}') {' '*81} --> OK"
                        )
            else:
                outcome.setdefault("info", []).append(
                    f"'{var_name}' not longitude coordinate variable"
                    )
                if verbose:
                    logging.info(
                        f"Variable:  {str(var_name):<15} is not "
                        f"longitude coordinate variable")
        else:
            outcome.setdefault("info", []).append(
                f"'{var_name}' not coordinate variable"
                )
            if verbose:
                logging.info(
                    f"Variable:  {str(var_name):<15} is not longitude "
                    f"coordinate variable"
                )
    return outcome


# Test 19. Check time coordinate.
@register(CONVENTION, "cf_time")
def cf_time_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check time coordinate.")
    outcome = {"status": 1}
    for var_name, nc_var in ds.variables.items():
        dimension_type = CFREF().identify_dimension_type(nc_var)
        if dimension_type == "T":
            calendar = getattr(nc_var, "calendar", "")
            if calendar:
                if calendar not in CFREF().cf_calendars:
                    outcome.setdefault("warnings", []).append(
                        f"Non standard value for attribute 'calendar' ('{calendar}') "
                        f"of variable '{var_name}' which is identified as a time "
                        f"variable. Should be one of {CFREF().cf_calendars}"
                    )
                    if verbose:
                        logging.warning(f"Non standard value for attribute "
                            f"'calendar' ('{calendar}') "
                            f"of variable '{var_name}' which is identified as a time "
                            f"variable. Should be one of {CFREF().cf_calendars}")
                # missing_month_length_msg = (
                #     f"Attribute 'month_length' is recommended when attribute "
                #     f"'calendar' has a non standard value. Missing for variable: "
                #     f"'{var_name}'"
                # )
                else:
                    if verbose:
                        outcome.setdefault("info", []).append(
                            f"'{var_name}' time coordinate variable OK"
                        )
                        logging.info(
                            f"Variable:  {str(var_name):<15} time "
                            f"coordinate variable --> calendar {' '*75} --> OK")

            else:
                if var_name != "leadtime":
                    outcome.setdefault("warnings", []).append(
                        f"Attribute 'calendar' is recommended for variables identified "
                        f"as time variables. Missing for '{var_name}'"
                        )
                    if verbose:
                            logging.warning(
                        f"Variable:  {str(var_name):<15} Attribute "
                        f"'calendar' is recommended for variables identified "
                        f"as time variables. Missing for '{var_name}'"
                        )
                else:
                    outcome.setdefault("info", []).append(
                       f"Attribute 'calendar' is recommended for variables identified "
                       f"as time variables. In C3S-0.1 is allowed for '{var_name}'"
                    )
                    if verbose:
                        logging.info(
                            f"Variable:  {str(var_name):<15} Attribute "
                            f"'calendar' is recommended for variables identified "
                            f"as time variables."
                        )
                        logging.info(
                            f"Variable:  {str(var_name):<15} in C3S-0.1 "
                            f"leadtime is the forecast step. No calendar is needed {' '*49} --> OK"
                        )
                if not getattr(nc_var, "month_length", ""):
                    if var_name != "leadtime":
                        outcome.setdefault("warnings", []).append(
                            f"Variable: {var_name} Attribute 'month_length' "
                            f"is recommended when attribute "
                            f"'calendar' is not declared. "
                            f"Missing for variable: '{var_name}'"
                        )
                        if verbose:
                            logging.warning(
                                f"Variable:  {str(var_name):<15} Attribute 'month_length' "
                                f"is recommended when attribute "
                                f"'calendar' is not declared. "
                                f"Missing for variable: '{var_name}'"
                            )
        else:
            outcome.setdefault("info", []).append(
                f"'{var_name}' not time coordinate variable"
            )
            if verbose:
                logging.info(
                    f"Variable:  {str(var_name):<15} is not time coordinate "
                    f"variable"
                )
    return outcome


# Test 20. Check coordinates.
@register(CONVENTION, "cf_coordinates")
def cf_coordinates_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check coordinates.")
    outcome = {"status": 1}
    for var_name, nc_var in ds.variables.items():
        coords = getattr(nc_var, "coordinates", "")
        status_flag = True
        if coords:
            for aux_coord in coords.split():
                if aux_coord not in ds.variables:
                    outcome["status"] = 0
                    status_flag = False
                    error_message = (
                        f"Variable '{aux_coord}' declared as auxiliary coordinate "
                        f"for variable '{var_name}' but inexistent in the dataset"
                    )
                    outcome.setdefault("errors", []).append(error_message)
                    if verbose:
                        logging.error(
                            f"Variable {str(aux_coord):<15} declared as auxiliary coordinate "
                            f"for variable {str(var_name):<15} but inexistent in the dataset "
                            f"{' '*23} --> NOK"
                        )
                else:
                    aux_coord_var = ds.variables[aux_coord]
                    dim_type = CFREF().identify_dimension_type(aux_coord_var)
                    if dim_type in ("X", "Y") and not set(
                        aux_coord_var.dimensions
                    ).issubset(set(nc_var.dimensions)):
                        outcome["status"] = 0
                        status_flag = False
                        error_message = (
                            f"Dimensions of 2-Dimensional auxiliary coordinate "
                            f"'{aux_coord}' are not part of dimensions of "
                            f"coordinate variable '{var_name}'"
                        )
                        outcome.setdefault("errors", []).append(error_message)
                        if verbose:
                            logging.error(error_message)
                    if dim_type in ("T", "X", "Y") and not set(
                        aux_coord_var.dimensions
                        ).issubset(set(nc_var.dimensions)):
                            outcome["status"] = 0
                            status_flag = False
                            outcome.setdefault("errors", []).append(
                                f"Dimensions of 3-Dimensional auxiliary coordinate "
                                f"'{aux_coord}' are not part of dimensions of "
                                f"coordinate variable '{var_name}'"
                            )
                            if verbose:
                                logging.error(
                                    f"Dimensions of 3-Dimensional auxiliary coordinate "
                                    f"'{aux_coord}' are not part of dimensions of "
                                    f"coordinate variable '{var_name}'"
                            )
                    if dim_type in ("T", "Z", "X", "Y") and not set(
                        aux_coord_var.dimensions
                        ).issubset(set(nc_var.dimensions)):
                            outcome["status"] = 0
                            status_flag = False
                            outcome.setdefault("errors", []).append(
                                f"Dimensions of 4-Dimensional auxiliary coordinate "
                                f"'{aux_coord}' are not part of dimensions of "
                                f"coordinate variable '{var_name}'"
                            )
                            if verbose:
                                logging.error(
                                    f"Dimensions of 4-Dimensional auxiliary coordinate "
                                    f"'{aux_coord}' are not part of dimensions of "
                                    f"coordinate variable '{var_name}'"
                                )
            if status_flag:
                outcome.setdefault("info", []).append(f"'{var_name}' coordinates OK")
                if verbose:
                    logging.info(
                        f"Variable:  {str(var_name):<15} coordinates: "
                        f"{str(coords):<80} {' '*19} --> OK"
                    )
        else:
            outcome.setdefault("info", []).append(f"'{var_name}' without coordinates")
            if verbose:
                logging.info(
                    f"Variable:  {str(var_name):<15} without "
                    f"coordinates {' '*93} --> OK"
                )
    return outcome


# Test 21. Check cell methods.
@register(CONVENTION, "cf_cell_methods")
def cf_cell_methods_check(ds: Dataset, _, excep: dict, verbose, operational):
    if verbose:
        logging.info("Check cell methods.")
    outcome = {"status": 1}    
    for var_name, nc_var in ds.variables.items():
        cell_methods = getattr(nc_var, "cell_methods", "")
        if cell_methods:
            match = CFREF().cf_cell_methods_pattern.match(cell_methods)
            if not match:
                outcome["status"] = 0
                error_message = (
                    f"Value of attribute cell_methods ('{cell_methods}') "
                    f"of variable '{var_name}' does not match the pattern "
                    f"for cell_methods: {CFREF().cf_cell_methods_pattern.pattern}"
                )
                outcome.setdefault("errors", []).append(error_message)
                if verbose:
                    logging.error(error_message)
            else:
                outcome.setdefault("info", []).append(f"'{var_name}' cell methods OK")
                if verbose:
                    logging.info(
                        f"Variable:  {str(var_name):<15} value of attribute "
                        f"cell_methods: {str(cell_methods):<70} {' '*9} --> OK"
                    )
        else:
            outcome.setdefault("info", []).append(f"'{var_name}' no cell methods") 
            if verbose:
                logging.info(
                    f"Variable:  {str(var_name):<15} no cell "
                    f"methods {' '*97} --> OK ")
            
    return outcome


def __get_std_name(std_name):
    components = std_name.split()
    if len(components) > 2:
        return None, None
    if len(components) == 2:
        return components[0], components[1]
    return components[0], None
