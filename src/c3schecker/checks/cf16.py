from pathlib import Path

from cfunits import Units
from netCDF4 import Dataset
import numpy as np

from c3schecker.checks import register
from c3schecker.utils import Singleton, powerset

CONVENTION = "CF-1.6"


@Singleton
class CFREF:
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
    global_attrs = (
        "title",
        "institution",
        "source",
        "history",
        "references",
        "comment",
    )

    def identify_dimension_type(self, dim_var):
        try:
            axis = dim_var.axis
            for axis_type in self.dimensions_order[1:]:
                if axis == axis_type:
                    return axis
        except AttributeError:
            pass
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
        unit = Units(dim_var.units)
        if unit.isreftime or unit.istime:
            return self.dimensions_order[1]
        try:
            if (
                unit.ispressure
                or dim_var.units in self.z_axis_units
                or dim_var.positive.lower() in ["up", "down"]
            ):
                return self.dimensions_order[2]
        except AttributeError:
            pass
        if unit.islongitude:
            return self.dimensions_order[3]
        if unit.islatitude:
            return self.dimensions_order[4]
        # Fall back to "*" (which means everything else)
        return self.dimensions_order[0]


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
    if actual not in CONVENTION:
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
