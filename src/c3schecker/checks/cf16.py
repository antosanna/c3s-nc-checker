import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from xml.etree import ElementTree

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
    cf_cell_methods_pattern = re.compile(
        r"^((?P<name>(\s*area|[\w_]+:\s+)+)(?P<method>(point|sum|mean|maximum|minimum"
        r"|mid_range|standard_deviation|variance|mode|median)"
        r"(\s+where\s+[\w_-]+(\s+over\s+[\w_-]+)?)?"
        r"(\s+\((((interval:\s[0-9]+(\.[0-9]+)?\s([a-zA-Z_]+|1))"
        r"(\s+interval:\s[0-9]+(\.[0-9]+)?\s([a-zA-Z_]+|1))*"
        r"(\s+comment:(\s[\w_-]+)+)?)|(([\w_-]+\s*)+))\))?))*$",
        re.VERBOSE,
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
        return np.issubdtype(nc_var.dtype, np.str)

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


@register(CONVENTION, "cf_filename_extension")
def cf_filename_extension_check(ds: Dataset, _):
    actual = Path(ds.filepath())
    if actual.suffix != ".nc":
        return {
            "status": 1,
            "warnings": [
                f"Non compliant filename extension: '{actual.suffix}'. Should be '.nc'"
            ],
        }
    return {"status": 1, "info": ["OK"]}


@register(CONVENTION, "cf_convention")
def cf_convention_check(ds: Dataset, _):
    actual = ds.Conventions
    if CONVENTION not in actual:
        return {
            "status": 0,
            "errors": [
                f"Current Convention metadata ('{actual}' is not compliant with "
                f"expected Convention: '{CONVENTION}'. See CF reference chapter 2.6.1"
            ],
        }
    return {"status": 1, "info": ["OK"]}


@register(CONVENTION, "cf_data_types")
def cf_datatypes_check(ds: Dataset, _):
    outcome = {"status": 1}
    for var_name, nc_var in ds.variables.items():
        actual = nc_var.dtype
        if actual not in CFREF().data_types:
            outcome.setdefault("errors", []).append(
                f"{var_name} has invalid data type '{actual}"
            )
            outcome["status"] = outcome["status"] and 0
        else:
            outcome.setdefault("info", []).append(f"{var_name} OK")
    return outcome


@register(CONVENTION, "cf_dimensions_order")
def cf_dimensions_order_check(ds: Dataset, _):
    outcome = {"status": 1}
    for var_name, variable in ds.variables.items():
        dims = variable.dimensions
        if len(dims) > 1:
            # Check dimensions order only for coordinate variables (i.e, dimensions that
            # are also considered to be variables with themselves as the sole dimension)
            try:
                dim_vars = [ds.variables[dim] for dim in dims]
            except KeyError:
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
            else:
                outcome.setdefault("info", []).append(f"'{var_name}' dimensions OK")
    return outcome


@register(CONVENTION, "cf_dimensions_unicity")
def cf_dimensions_unicity_check(ds: Dataset, _):
    outcome = {"status": 1}
    for var_name, variable in ds.variables.items():
        dims = variable.dimensions
        dims_count = [dims.count(dim) for dim in dims]
        if any(c > 1 for c in dims_count):
            outcome.setdefault("errors", []).append(
                f"'{var_name}' has duplicate dimensions: {dims}"
            )
            outcome["status"] = 0
    return outcome


@register(CONVENTION, "cf_global_attributes")
def cf_global_attributes_check(ds: Dataset, _):
    outcome = {"status": 1}
    global_attrs = set(ds.ncattrs())
    recommended = set(CFREF().global_attrs)
    intersect = global_attrs.intersection(recommended)
    missing = recommended - intersect
    if missing:
        outcome.setdefault("warnings", []).append(
            f"Some recommended global attributes are missing: {list(missing)}"
        )
    for attr in global_attrs:
        attr_value = ds.getncattr(attr)
        if not isinstance(attr_value, str):
            outcome.setdefault("errors", []).append(
                f"Global attributes '{attr}' is not a string. Found type "
                f"'{type(attr_value)}' instead"
            )
            outcome["status"] = 0
    return outcome


@register(CONVENTION, "cf_missing_data")
def cf_missing_data_check(ds: Dataset, _):
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
        else:
            if "valid_range" in attrs:
                _, vmax = nc_var.getncattr("valid_range")
            elif "valid_max" in attrs:
                vmax = nc_var.getncattr("valid_max")
            else:
                vmax = None
            if vmax is not None:
                vmax = np.array(vmax, dtype=nc_var.dtype)
                fill_value = nc_var[:1].fill_value
                if fill_value <= vmax:
                    outcome["status"] = 0
                    outcome.setdefault("errors", []).append(
                        f"Fill value '{fill_value}' is lower than valid max '{vmax}' "
                        f"for variable '{var_name}'"
                    )
        fvalue_type = nc_var[:1].fill_value.dtype
        if nc_var.dtype != fvalue_type:
            outcome.setdefault("warnings", []).append(
                f"Variable '{var_name}' type ({nc_var.dtype}) differs from fill "
                f"value type ({fvalue_type})"
            )
    return outcome


@register(CONVENTION, "cf_naming_convention")
def cf_naming_convention_check(ds: Dataset, _):
    outcome = {"status": 1}
    naming_convention = re.compile("[a-zA-Z][a-zA-Z0-9_]*")

    def _check(name, err_msg):
        if not naming_convention.match(name):
            outcome["status"] = 0
            outcome.setdefault("errors", []).append(err_msg)

    for var_name, nc_var in ds.variables.items():
        _check(
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
                _check(
                    attribute,
                    (
                        f"Attribute '{attribute}' of variable '{var_name}' does not "
                        f"follow naming convention '{naming_convention.pattern}'"
                    ),
                )
    for global_attribute in ds.ncattrs():
        if global_attribute != "_FillValue":
            _check(
                global_attribute,
                (
                    f"Global attribute '{global_attribute}' does not follow naming "
                    f"convention '{naming_convention.pattern}'"
                ),
            )
    return outcome


@register(CONVENTION, "cf_naming_unicity")
def cf_naming_unicity_check(ds: Dataset, _):
    outcome = {"status": 1}
    ds_names = Counter(k.lower() for k in ds.variables)
    for name, count in ds_names.items():
        if count > 1:
            outcome["status"] = 0
            outcome.setdefault("errors", []).append(
                f"Variable '{name}' is not unique. Found {count} occurrences in "
                f"the dataset"
            )
    return outcome


@register(CONVENTION, "cf_ancillary_data")
def cf_ancillary_data_check(ds: Dataset, _):
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
            else:
                for anc_var in anc_vars.split():
                    if anc_var not in variables:
                        outcome["status"] = 0
                        outcome.setdefault("errors", []).append(
                            f"Variable '{anc_var}' is declared as Ancillary Variable "
                            f"for '{var_name}' but is not defined in the dataset"
                        )
        except AttributeError:
            pass
    return outcome


@register(CONVENTION, "cf_standard_names")
def cf_standard_names_check(ds: Dataset, _):
    outcome = {"status": 1}
    for var_name, nc_var in ds.variables.items():
        attrs = nc_var.ncattrs()
        if (
            all(attr not in attrs for attr in ["standard_name", "long_name"])
            and not CFREF.is_cf_boundary_variable(nc_var)
            and not CFREF.is_cf_label_variable(nc_var)
        ):
            outcome.setdefault("warnings", []).append(
                f"Variable description with 'long_name' and 'standard_name' "
                f"attributes is highly recommended. None found for variable "
                f"'{var_name}'"
            )
        try:
            std_name, modifier = __get_std_name(nc_var.getncattr("standard_name"))
            if not isinstance(std_name, str):
                outcome.setdefault("errors", []).append(
                    f"Attribute 'standard_name' of variable '{var_name}' must be a "
                    f"string. Currently '{type(std_name)}'"
                )
            else:
                if std_name is None and modifier is None:
                    outcome["status"] = 0
                    outcome.setdefault("errors", []).append(
                        f"Only two blank separated names allowed for attribute "
                        f"'standard_name' of variable '{var_name}'. Currently "
                        f"{len(nc_var.getncattr('standard_name').split())}"
                    )
                else:
                    _ = CFREF().cf_standard_name_def(std_name)
                    if (
                        modifier is not None
                        and modifier not in CFREF().cf_units_modifiers
                    ):
                        outcome["status"] = 0
                        outcome.setdefault("errors", []).append(
                            f"Standard name modifier for variable '{var_name}' "
                            f"({modifier}) is not a recognized CF standard name "
                            f"modifier"
                        )
        except AttributeError:
            pass
        except UnknownStandardNameError:
            outcome.setdefault("warnings", []).append(
                f"Attribute 'standard_name' of variable '{var_name}' ({std_name}) "
                f"is not a recognized CF standard name"
            )
    return outcome


@register(CONVENTION, "cf_units")
def cf_units_check(ds: Dataset, _):
    outcome = {"status": 1}
    for var_name, nc_var in ds.variables.items():
        attrs = nc_var.ncattrs()
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
                    outcome.setdefault("errors", []).append(
                        f"Attribute 'units' of variable '{var_name}' must be a string "
                        f"(currently '{type(units_attr)}'"
                    )
                elif units_attr in CFREF.deprecated_units:
                    outcome.setdefault("warnings", []).append(
                        f"Value of attribute 'units' of variable '{var_name}' is "
                        f"deprecated: '{units_attr}'. No further checks done."
                    )
                else:
                    units = Units(units_attr)
                    if not units.isvalid:
                        outcome["status"] = 0
                        outcome.setdefault("errors", []).append(
                            f"Value of attribute 'units' of variable '{var_name}' is "
                            f"invalid: '{units}'"
                        )
                    elif "standard_name" in attrs:
                        std_name, modifier = __get_std_name(
                            nc_var.getncattr("standard_name")
                        )
                        if std_name is None:
                            outcome.setdefault("warnings", []).append(
                                "Further units checking skipped due to invalid "
                                "standard name"
                            )
                        else:
                            known_units = Units(
                                CFREF().cf_standard_name_def(std_name)["units"]
                            )
                            if not known_units.isvalid:
                                outcome["status"] = 0
                                outcome.setdefault("errors", []).append(
                                    f"Units of variable '{var_name}' ('{units}') "
                                    f"cannot be compared with standard name canonical "
                                    f"units because the canonical units is invalid "
                                    f"('{known_units}')"
                                )
                            else:
                                known_units = Units(
                                    CFREF.cf_units_modifiers.get(modifier, known_units)
                                )
                                if units.isreftime:
                                    units = Units(units_attr.split()[0])
                                if not units.equivalent(known_units):
                                    outcome["status"] = 0
                                    outcome.setdefault("errors", []).append(
                                        f"Units of variable '{var_name}' ('{units}') "
                                        f"is not consistent with standard name "
                                        f"canonical units ('{known_units}')"
                                    )
    return outcome


@register(CONVENTION, "cf_flags")
def cf_flags_check(ds: Dataset, _):
    outcome = {"status": 1}
    flag_meanings_pattern = re.compile("^[0-9A-Za-z_\-@+.]+$")
    for var_name, nc_var in ds.variables.items():
        attrs = nc_var.ncattrs()
        if "standard_name" in attrs:
            std_name, modifier = __get_std_name(nc_var.getncattr("standard_name"))
            if std_name is None:
                outcome.setdefault("warnings", []).append(
                    "Further flags checking skipped due to invalid standard name"
                )
            else:
                if (
                    modifier in (m for m in CFREF().cf_units_modifiers if "flag" in m)
                    and "flag_meanings" not in attrs
                ):
                    outcome["status"] = 0
                    outcome.setdefault("errors", []).append(
                        f"Standard name modified to a flag but no 'flag_meanings' "
                        f"found in attributes for variable '{var_name}'"
                    )
        if "flag_meanings" in attrs and all(
            a not in attrs for a in ["flag_values", "flag_masks"]
        ):
            outcome["status"] = 0
            outcome.setdefault("errors", []).append(
                f"Attribute 'flag_meanings' is defined for variable '{var_name}' but "
                f"neither 'flag_values' nor 'flag_masks' are defined"
            )
        elif "flag_meanings" not in attrs and any(
            a in attrs for a in ["flag_values", "flag_masks"]
        ):
            outcome["status"] = 0
            outcome.setdefault("errors", []).append(
                f"Attribute 'flag_meanings' is missing for variable '{var_name}' "
                f"although either 'flag_values' or 'flag_masks' attributes are defined"
            )
        elif "flag_meanings" in attrs:
            flag_meanings = nc_var.getncattr("flag_meanings")
            if not isinstance(flag_meanings, str):
                outcome["status"] = 0
                outcome.setdefault("errors", []).append(
                    f"Value of attribute '{flag_meanings}' must be a string. Found "
                    f"'{type(flag_meanings)}' instead"
                )
            elif not all(
                flag_meanings_pattern.match(item) for item in flag_meanings.split()
            ):
                outcome["status"] = 0
                outcome.setdefault("errors", []).append(
                    f"Incorrect Syntax for flag_meanings attribute value of "
                    f"variable '{var_name}': '{flag_meanings}'. Must be: "
                    f"'{flag_meanings_pattern}'"
                )
            if "flag_values" in attrs:
                flag_values = np.array(nc_var.getncattr("flag_values"))
                if not np.issubdtype(flag_values.dtype, nc_var.dtype):
                    outcome["status"] = 0
                    outcome.setdefault("errors", []).append(
                        f"Values of attribute for 'flag_values' must have the same type "
                        f"as variable '{var_name}'. Found '{flag_values.dtype}' instead"
                    )
                elif len(flag_values) != len(flag_meanings):
                    outcome["status"] = 0
                    outcome.setdefault("errors", []).append(
                        f"Attribute 'flag_values' of variable '{var_name}' must have "
                        f"the same number of elements as attribute 'flag_meanings'"
                    )
                elif len(flag_values) != len(set(flag_values)):
                    outcome["status"] = 0
                    outcome.setdefault("errors", []).append(
                        f"Values for attribute 'flag_values' of variable '{var_name}' "
                        f"must be unique"
                    )
            if "flag_masks" in attrs:
                flag_masks = np.array(nc_var.getncattr("flag_masks"))
                if not np.issubdtype(flag_masks.dtype, nc_var.dtype):
                    outcome["status"] = 0
                    outcome.setdefault("errors", []).append(
                        f"Values of attribute 'flag_masks' must have the same type "
                        f"as variable '{var_name}'. Found '{flag_masks.dtype}' instead"
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
                    outcome.setdefault("errors", []).append(
                        f"Variable '{var_name}' type is not appropriate for flag "
                        f"masking ('{nc_var.dtype}'). Must be one of {expected}"
                    )
                elif len(flag_masks) != len(flag_meanings):
                    outcome["status"] = 0
                    outcome.setdefault("errors", []).append(
                        f"Attribute 'flag_masks' of variable '{var_name}' must have "
                        f"the same number of elements as attribute 'flag_meanings'"
                    )
                elif np.count_nonzero(flag_masks) != flag_masks.size:
                    outcome["status"] = 0
                    outcome.setdefault("errors", []).append(
                        f"Attribute 'flag_masks' of variable '{var_name}' must have "
                        f"only non zero elements in its values. Currently "
                        f"{np.count_nonzero(flag_masks)} zero values"
                    )
                elif "flag_values" in attrs:
                    flag_values = np.array(nc_var.getncattr("flag_values"))
                    for mask in flag_masks:
                        if np.count_nonzero((nc_var[:] & mask) == flag_values) == 0:
                            outcome["status"] = 0
                            outcome.setdefault("errors", []).append(
                                f"Bitwise AND of flag_masks value '{mask}' and "
                                f"'{var_name}' values results in a value not "
                                f"available in attribute 'flag_values'. Must result"
                                f" in '{flag_values}'"
                            )
    return outcome


@register(CONVENTION, "cf_coordinates_variables")
def cf_coordinates_variables_check(ds: Dataset, _):
    outcome = {"status": 1}
    nc_variables = ds.variables.values()
    for var_name, nc_var in zip(ds.variables, nc_variables):
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
                        outcome.setdefault("errors", []).append(
                            f"Coordinate variables must have units or have their "
                            f"standard_name in the list of dimensionless vertical "
                            f"coordinates"
                        )
                except AttributeError:
                    pass
            else:
                try:
                    positive = nc_var.getncattr("positive")
                    if positive.lower() not in CFREF().z_axis_orientations:
                        outcome["status"] = 0
                        outcome.setdefault("errors", []).append(
                            f"Value of 'positive' attribute ({positive}) is not allowed. "
                            f"Use one of '{CFREF().z_axis_orientations}' instead"
                        )
                except AttributeError:
                    pass
                dimension_type = CFREF().identify_dimension_type(nc_var)
                axis = getattr(nc_var, "axis", "")
                if dimension_type == "*":
                    if axis == "E":
                        outcome.setdefault("warnings", []).append(
                            f"Axis E of coordinate '{var_name}' is not part of "
                            f"CF-1.6 but may be allowed in CF 1.7"
                        )
                    elif not axis:
                        outcome.setdefault("warnings", []).append(
                            f"Axis attribute not provided for coordinate variable"
                            f" '{var_name}'"
                        )
                    else:
                        outcome["status"] = 0
                        outcome.setdefault("errors", []).append(
                            f"Unsupported value of attribute 'axis' for coordinate "
                            f"variable '{var_name}': '{axis}'. Should be one of "
                            f"'{CFREF().dimensions_order[1:] + ('E',)}'"
                        )
                else:
                    if axis != dimension_type and unit != "1":
                        outcome["status"] = 0
                        outcome.setdefault("errors", []).append(
                            f"Attribute 'axis' of coordinate variable '{var_name}' "
                            f"is not consistent with unit '{unit}'"
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
            if positive:
                outcome.setdefault("warnings", []).append(
                    f"Value of attribute 'positive' of variable '{var_name}' "
                    f"('{positive}') may not be allowed because variable is not "
                    f"identified as a coordinate variable"
                )
    return outcome


@register(CONVENTION, "cf_dimensionless_vertical_coordinates")
def cf_dimensionless_vertical_coordinates_check(ds: Dataset, _):
    outcome = {"status": 1}
    for var_name, nc_var in ds.variables.items():
        try:
            std_name = nc_var.getncattr("standard_name")
            regex = CFREF().dimensionless_vertical_coordinates.get(std_name)
            if regex and not regex.match(nc_var.getncattr("formula_terms")):
                outcome["status"] = 0
                outcome.setdefault("errors", []).append(
                    f"Value of attribute 'formula_terms' of variable '{var_name}' "
                    f"does not match the known pattern for this standard_name "
                    f"'{std_name}'. Must match: '{regex}' (Python Regex)"
                )
        except AttributeError:
            pass
    return outcome


@register(CONVENTION, "cf_latitude")
def cf_latitude_check(ds: Dataset, _):
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
    return outcome


@register(CONVENTION, "cf_longitude")
def cf_longitude_check(ds: Dataset, _):
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
    return outcome


@register(CONVENTION, "cf_time")
def cf_time_check(ds: Dataset, _):
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
                missing_month_length_msg = (
                    f"Attribute 'month_length' is recommended when attribute "
                    f"'calendar' has a non standard value. Missing for variable: "
                    f"'{var_name}'"
                )
            else:
                outcome.setdefault("warnings", []).append(
                    f"Attribute 'calendar' is recommended for variables identified "
                    f"as time variables. Missing for '{var_name}'"
                )
                missing_month_length_msg = (
                    f"Attribute 'month_length' is recommended when attribute "
                    f"'calendar' is not declared. Missing for variable: '{var_name}'"
                )
            if not getattr(nc_var, "month_length", ""):
                outcome.setdefault("warnings", []).append(missing_month_length_msg)
    return outcome


@register(CONVENTION, "cf_coordinates")
def cf_coordinates_check(ds: Dataset, _):
    outcome = {"status": 1}
    for var_name, nc_var in ds.variables.items():
        coords = getattr(nc_var, "coordinates", "")
        if coords:
            for aux_coord in coords.split():
                if aux_coord not in ds.variables:
                    outcome["status"] = 0
                    outcome.setdefault("errors", []).append(
                        f"Variable '{aux_coord}' declared as auxiliary coordinate "
                        f"for variable '{var_name}' but inexistent in the dataset"
                    )
                else:
                    aux_coord_var = ds.variables[aux_coord]
                    dim_type = CFREF().identify_dimension_type(aux_coord_var)
                    if dim_type in ("X", "Y") and not set(
                        aux_coord_var.dimensions
                    ).issubset(set(nc_var.dimensions)):
                        outcome["status"] = 0
                        outcome.setdefault("errors", []).append(
                            f"Dimensions of 2-Dimensional auxiliary coordinate "
                            f"'{aux_coord}' are not part of dimensions of "
                            f"coordinate variable '{var_name}'"
                        )
    return outcome


@register(CONVENTION, "cf_cell_methods")
def cf_cell_methods_check(ds: Dataset, _):
    outcome = {"status": 1}
    for var_name, nc_var in ds.variables.items():
        cell_methods = getattr(nc_var, "cell_methods", "")
        if cell_methods:
            match = CFREF().cf_cell_methods_pattern.match(cell_methods)
            if not match:
                outcome["status"] = 0
                outcome.setdefault("errors", []).append(
                    f"Value of attribute cell_methods ('{cell_methods}') "
                    f"of variable '{var_name}' does not match the pattern "
                    f"for cell_methods: {CFREF().cf_cell_methods_pattern.pattern}"
                )
    return outcome


def __get_std_name(std_name):
    components = std_name.split()
    if len(components) > 2:
        return None, None
    if len(components) == 2:
        return components[0], components[1]
    return components[0], None
