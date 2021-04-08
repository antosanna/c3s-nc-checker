import datetime
import re

import numpy as np
from c3schecker.checks import register
from netCDF4 import Dataset
from numpy.ma import MaskedArray


CONVENTION = "C3S-0.1"
NUMBER_REGEX = re.compile(r"^[-+]?[0-9]+.?[0-9]*$")


@register(CONVENTION, "md_convention")
def c3s_meta_convention_check(ds: Dataset, spec: dict) -> dict:
    constraints = spec.get("convention", {})
    err_msgs = [
        (
            "Global Metadata *Conventions* must be set to '{expected}'. "
            "Currently: '{actual}'"
        )
    ]
    warn_msgs = [
        (
            "Global Metadata *Conventions* must be set to '{expected}' "
            "(Not Mandatory). Currently: '{actual}'"
        )
    ]
    actual = ds.Conventions
    return _simple_equality_check(actual, constraints, warn_msgs, err_msgs)


@register(CONVENTION, "md_netcdf_format")
def c3s_meta_netcdf_format_check(ds: Dataset, spec: dict) -> dict:
    constraints = spec.get("netcdf_format", {})
    err_msgs = [
        "NetCDF *file_format* must be set to '{expected}'. " "Currently: '{actual}'"
    ]
    warn_msgs = [
        (
            "NetCDF *file_format* must be set to '{expected}' (Not Mandatory). "
            "Currently: '{actual}'"
        )
    ]
    actual = ds.file_format
    return _simple_equality_check(actual, constraints, warn_msgs, err_msgs)


@register(CONVENTION, "md_number_data_var_per_file")
def c3s_meta_number_data_var_per_file(ds: Dataset, spec: dict) -> dict:
    # Data vars are scientific data discretized over a domain. The domain is defined
    # by a set of coordinate variables. Data vars therefore depend on coordinate
    # variables, so they have a coordinates attributes. And they are the only ones
    # that can have that on a netCDF files (at least one which follows CF-convention).
    # That is what's used here to check that a ds only have the specified number of
    # data variables
    def _get_data_vars(dataset):
        return dataset.get_variables_by_attributes(coordinates=_ncattr_present)

    constraints = spec.get("nb_data_var_per_file", {})
    err_msgs = [
        "Only {expected} data variables must be contained in a single file. "
        "Currently: '{actual}'"
    ]
    warn_msgs = [
        (
            "{expected} data variables are expected to be contained in a single file "
            "(Not Mandatory). Currently: '{actual}'"
        )
    ]
    actual_data_vars = _get_data_vars(ds)
    return _simple_equality_check(
        len(actual_data_vars), constraints, warn_msgs, err_msgs
    )


@register(CONVENTION, "md_dimensions")
def c3s_meta_dimensions_checks(ds: Dataset, spec: dict) -> dict:
    constraints = spec.get("dimensions", {})
    status = 1
    if not constraints:
        return {"status": status, "info": ["No constraints -> Skipped"]}
    err_msgs = []
    warn_msgs = []
    error_msg_pattern = "NetCDF Dimension {} is mandatory but absent from {}"
    warning_msg_pattern = "NetCDF Dimension {} is desirable but absent from {}"
    if not constraints.get("mandatory", True):
        msgs = warn_msgs
        msg_pattern = warning_msg_pattern
    else:
        msgs = err_msgs
        msg_pattern = error_msg_pattern

    actual_dimensions = list(ds.dimensions.keys())
    expected_dimensions = constraints["expected"]
    for dim in expected_dimensions:
        if dim not in actual_dimensions:
            msgs.append(msg_pattern.format(dim, actual_dimensions))

    # Only test for authorized dimensions if the actual count of dimensions exceeds
    # the count of expected mandatory dimensions
    rest = set(expected_dimensions) - set(actual_dimensions)
    if rest:
        authorized_dims = constraints.get("authorized", [])
        if authorized_dims:
            not_authorized = set(authorized_dims) - set(rest)
            if not_authorized:
                msgs.append(
                    f"Dataset Dimensions {list(not_authorized)} are neither in the "
                    f"desirable/mandatory nor authorized dimensions ({authorized_dims})"
                )
    outcome = {}
    if warn_msgs:
        outcome["warnings"] = warn_msgs
    elif err_msgs:
        status = 0
        outcome["errors"] = err_msgs
    else:
        outcome["info"] = ["OK"]
    outcome["status"] = status
    return outcome


@register(CONVENTION, "md_attributes_per_var_name")
def c3s_meta_attributes_per_var_name(ds: Dataset, spec: dict) -> dict:
    overall_constraints = spec.get("attributes_per_var_names", {})
    if not overall_constraints:
        return {"status": 1, "info": ["No constraints -> Skipped"]}

    outcome = {"status": 1}
    for var_name, constraints in overall_constraints.items():
        expected = constraints["expected"]
        query = {"name": var_name}
        query.update({attr: _ncattr_present for attr in expected})
        result = ds.get_variables_by_attributes(**query)
        if len(result) == 1:
            outcome.setdefault("info", []).append(f"{var_name}: OK")
        else:
            variable = ds.variables.get(var_name)
            if variable is not None:
                if constraints.get("mandatory", True):
                    message_type = "errors"
                    new_status = 0
                else:
                    message_type = "warnings"
                    new_status = 1
                outcome.get(message_type, []).append(
                    f"{var_name} is missing mandatory attributes. "
                    f"Expected: {expected}; Actual: {variable.ncattrs()}"
                )
                outcome["status"] = outcome["status"] and new_status
    return outcome


@register(CONVENTION, "md_allowed_attributes_values")
def c3s_meta_attributes_possible_values(ds: Dataset, spec: dict) -> dict:
    overall_constraints = spec.get("possible_values_per_attributes", {})
    outcome = {"status": 1}
    for attr_name, constraints in overall_constraints.items():
        query = {attr_name: _ncattr_present}
        vars_with_attr = ds.get_variables_by_attributes(**query)
        possible_values = constraints["expected"]
        for variable in vars_with_attr:
            actual_value = getattr(variable, attr_name)
            if actual_value in possible_values:
                outcome.setdefault("info", []).append(
                    f"{variable.name}->{attr_name}: OK"
                )
            else:
                if constraints.get("mandatory", True):
                    message_type = "errors"
                    new_status = 0
                else:
                    message_type = "warnings"
                    new_status = 1
                outcome.setdefault(message_type, []).append(
                    f"Attribute '{attr_name}' value for '{variable.name}'"
                    f"({actual_value}) is not allowed. "
                    f"Possible values: {possible_values}"
                )
                outcome["status"] = outcome["status"] and new_status
    return outcome


@register(CONVENTION, "md_exact_attributes_values")
def c3s_meta_attributes_exact_values_per_var_name(ds: Dataset, spec: dict) -> dict:
    overall_constraints = spec.get("attributes_values_per_var_name", {})
    outcome = {"status": 1}
    # Some of the attribute values should be checked against a regular expression
    check_regex = ["cell_methods"]
    for var_name, nc_var in ds.variables.items():
        var_specific_constraints = overall_constraints.get(var_name, {})
        for attr_name, expected_value in var_specific_constraints.get(
            "expected", {}
        ).items():
            try:
                actual_value = str(nc_var.getncattr(attr_name))
                # Does the actual value look like a number?
                if NUMBER_REGEX.match(actual_value):
                    # If yes, convert it to the type of the referring var
                    actual_value = np.array(
                        nc_var.getncattr(attr_name), dtype=nc_var.dtype
                    )
            except AttributeError:
                outcome.setdefault("errors", []).append(
                    f"Variable '{var_name}' is missing attribute '{attr_name}'"
                )
                outcome["status"] = 0
                continue
            if attr_name not in check_regex:
                if NUMBER_REGEX.match(str(expected_value)):
                    expected_value = np.array(expected_value, dtype=nc_var.dtype)
                check_result = actual_value == expected_value
            else:
                check_result = re.match(expected_value, actual_value)
            if check_result:
                outcome.setdefault("info", []).append(f"{var_name}->{attr_name}: OK")
            else:
                if var_specific_constraints.get("mandatory", True):
                    message_type = "errors"
                    new_status = 0
                else:
                    message_type = "warnings"
                    new_status = 1
                outcome.setdefault(message_type, []).append(
                    f"Attribute '{attr_name}' of variable '{var_name}' ({actual_value})"
                    f" is not allowed. Expected: {expected_value}"
                )
                outcome["status"] = outcome["status"] and new_status
    return outcome


@register(CONVENTION, "md_global_attributes")
def c3s_meta_global_attributes(ds: Dataset, spec: dict) -> dict:
    constraints = spec.get("global_attributes", {})
    if not constraints:
        return {"status": 1, "info": ["No constraints -> Skipped"]}
    actual = set(sorted(ds.ncattrs()))
    expected = set(sorted(constraints["expected"]))
    missing = expected - actual
    if not missing:
        outcome = {"status": 1, "info": ["OK"]}
    else:
        if constraints.get("mandatory", True):
            level = "errors"
            status = 0
        else:
            level = "warnings"
            status = 1
        outcome = {
            "status": status,
            level: [
                f"Some global attributes are missing from the list {list(expected)}: "
                f"{list(missing)}."
            ],
        }
    return outcome


@register(CONVENTION, "md_possible_global_attributes_values")
def c3s_meta_global_attributes_possible_values(ds: Dataset, spec: dict) -> dict:
    constraints = spec.get("global_attributes_possible_values", {})
    if not constraints:
        return {"status": 1, "info": ["No constraints -> Skipped"]}
    outcome = {"status": 1}
    mandatory_constraints = constraints.get("mandatory", True)
    for attr_name, possible_values in constraints["expected"].items():
        try:
            actual_value = getattr(ds, attr_name)
        except AttributeError:
            outcome.setdefault("errors", []).append(
                f"Dataset is missing global attribute '{attr_name}'"
            )
            outcome["status"] = 0
            continue
        if actual_value in possible_values:
            outcome.setdefault("info", []).append(f"{attr_name}: OK")
            status = 1
        else:
            if mandatory_constraints:
                message_type = "errors"
                status = 0
            else:
                message_type = "warnings"
                status = 1
            outcome.setdefault(message_type, []).append(
                f"Global Attribute '{attr_name}' value ({actual_value}) is not allowed."
                f" Possible values: {possible_values}"
            )
        outcome["status"] = outcome["status"] and status
    return outcome


@register(CONVENTION, "md_global_date_attributes_format")
def c3s_meta_global_attributes_date_format(ds: Dataset, spec: dict) -> dict:
    constraints = spec.get("global_attributes_date_format", {})
    if not constraints:
        return {"status": 1, "info": ["No constraints -> Skipped"]}
    outcome = {"status": 1}
    mandatory_constraints = constraints.get("mandatory", True)
    for date_attr_name, expected_date_attr_format in constraints["expected"].items():
        actual_date_attr_value = ds.getncattr(date_attr_name)
        try:
            datetime.datetime.strptime(
                actual_date_attr_value, expected_date_attr_format
            )
            status = 1
            outcome.setdefault("info", []).append(f"{date_attr_name}: OK")
        except ValueError:
            if mandatory_constraints:
                status = 0
                level = "errors"
            else:
                status = 0
                level = "warnings"
            outcome.setdefault(level, []).append(
                f"Global date Attribute '{date_attr_name}' value does not follow "
                f"required date format ({expected_date_attr_format})"
            )
        outcome["status"] = status
    return outcome


@register(CONVENTION, "md_variables_exact_dimensions")
def c3s_meta_variables_exact_dimensions(ds: Dataset, spec: dict) -> dict:
    constraints = spec.get("variables_exact_dimensions", {})
    if not constraints:
        return {"status": 1, "info": ["No constraints -> Skipped"]}
    outcome = {"status": 1}
    mandatory_constraints = constraints.get("mandatory", True)
    for var_name, expected_dimensions in constraints["expected"].items():
        try:
            actual_dimensions = set(ds.variables[var_name].dimensions)
        except KeyError:
            continue
        missing_dimensions = set(expected_dimensions) - actual_dimensions
        if missing_dimensions:
            if mandatory_constraints:
                status = 0
                level = "errors"
            else:
                status = 0
                level = "warnings"
            msg = (
                f"Missing dimensions {list(missing_dimensions)} for variable "
                f"'{var_name}'. Expected: {expected_dimensions}"
            )
        else:
            status = 1
            level = "info"
            msg = f"{var_name}: OK"
        outcome.setdefault(level, []).append(msg)
        outcome["status"] = status
    return outcome


@register(CONVENTION, "md_grib_consistency")
def c3s_meta_grib_consistency(ds: Dataset, spec: dict) -> dict:
    constraints = spec.get("grib_consistency", {})
    if not constraints:
        return {"status": 1, "info": ["No constraints -> Skipped"]}
    outcome = {"status": 1}
    mandatory_constraints = constraints.get("mandatory", True)
    for mars_paramid, expected_bindings in constraints["expected"].items():
        query = {"mars_paramid": mars_paramid}
        nc_var = ds.get_variables_by_attributes(**query)
        if nc_var:
            mars_param_name = expected_bindings["name"]
            for attr_name, expected in expected_bindings["cf"].items():
                actual_value = nc_var[0].getncattr(attr_name)
                if actual_value == expected:
                    status = 1
                    msg = f"mars id {mars_paramid}: OK"
                    level = "info"
                else:
                    if mandatory_constraints:
                        status = 0
                        level = "errors"
                    else:
                        status = 1
                        level = "warnings"
                    msg = (
                        f"Attribute '{attr_name}' of variable '{nc_var.name}' has "
                        f"an inconsistent value ('{actual_value}') wrt MARS paramid "
                        f"'{mars_paramid}' (name={mars_param_name}). Value should "
                        f"be: '{expected}'"
                    )
                outcome["status"] = status
                outcome.setdefault(level, []).append(msg)
    return outcome


@register(CONVENTION, "data_intervals")
def c3s_data_intervals(ds: Dataset, spec: dict) -> dict:
    ko_msg = (
        "Not matching intervals found for '{var_name}' "
        "dimension '{dim_name}': {bad_intervals}"
    )
    ok_msg = "{var_name} (dimension {dim_name}): OK"

    def logic(data, var_name, expected, dim_name=None):
        # Determine wether the logic is done on the dimension variable or otherwise
        if dim_name is None:
            dim_name = name = var_name
        else:
            name = dim_name
        dim_values = data.variables[name]
        all_intervals = dim_values[1:] - dim_values[:-1]
        not_matching_intervals = all_intervals[
            np.asarray(all_intervals != expected).nonzero()
        ]
        results = {
            "var_name": var_name,
            "dim_name": dim_name,
            "bad_intervals": list(not_matching_intervals),
            "failure": not_matching_intervals.any(),
        }
        return results

    return _data_check("data_intervals", ds, spec, logic, ko_msg, ok_msg)


@register(CONVENTION, "data_min_max")
def c3s_data_min_max(ds: Dataset, spec: dict) -> dict:
    ko_msg = (
        "Invalid min/max found for '{var_name}' (dimension '{dim_name}'): "
        "min={actual_min}, max={actual_max}. Expected: min={valid_min}, "
        "max={actual_max}"
    )
    ok_msg = "{var_name} (dimension: {dim_name}): OK"

    def logic(data, var_name, expected, dim_name=None):
        # Determine wether the logic is done on the dimension variable or otherwise
        if dim_name is None:
            dim_name = name = var_name
        else:
            name = dim_name
        dim_values = data.variables[name][:]
        expected_min, expected_max = expected
        actual_min, actual_max = dim_values.min(), dim_values.max()
        results = {
            "var_name": var_name,
            "dim_name": dim_name,
            "actual_min": actual_min,
            "actual_max": actual_max,
            "valid_min": expected_min,
            "valid_max": expected_max,
            "failure": (actual_min != expected_min or actual_max != expected_max),
        }
        return results

    return _data_check("data_min_max", ds, spec, logic, ko_msg, ok_msg)


@register(CONVENTION, "data_ranges")
def c3s_data_ranges(ds: Dataset, spec: dict) -> dict:
    ko_msg = (
        "Data out of valid range found for '{var_name}' (dimension '{dim_name}'): "
        "{out_of_range}. Expected Range: [{bot}, {top}]"
    )
    ok_msg = "{var_name} (dimension {dim_name}): OK"

    def logic(data, var_name, expected, dim_name=None):
        # Determine wether the logic is done on the dimension variable or otherwise
        if dim_name is None:
            dim_name = name = var_name
        else:
            name = dim_name
        values = data.variables[name][:]
        bottom, top = expected
        if isinstance(values, MaskedArray):
            # We don't want masked values to pollute our conformity test
            values = values[~values.mask]
        out_of_range = values[np.logical_or(values < bottom, values > top).nonzero()]
        results = {
            "var_name": var_name,
            "dim_name": dim_name,
            "bot": bottom,
            "top": top,
            "out_of_range": list(out_of_range),
            "failure": out_of_range.any(),
        }
        return results

    return _data_check("data_ranges", ds, spec, logic, ko_msg, ok_msg)


@register(CONVENTION, "data_values")
def c3s_data_values(ds: Dataset, spec: dict) -> dict:
    ko_msg = (
        "Invalid values found for '{var_name}' (dimension '{dim_name}'): "
        "{invalid_values}. Expected: {valid_values}"
    )
    ok_msg = "{var_name} (dimension {dim_name}): OK"

    def logic(data, var_name, expected, dim_name=None):
        # Determine wether the logic is done on the dimension variable or otherwise
        if dim_name is None:
            dim_name = name = var_name
        else:
            name = dim_name
        expected = np.array(expected)
        values = data.variables[name][:]
        if isinstance(values, MaskedArray):
            # Get non masked values as a 1D array
            values = values.compressed()
        unauthorized_values = values[np.asarray((values - expected) != 0).nonzero()]
        results = {
            "var_name": var_name,
            "dim_name": dim_name,
            "valid_values": expected,
            "invalid_values": list(unauthorized_values),
            "failure": unauthorized_values.any(),
        }
        return results

    return _data_check("data_values", ds, spec, logic, ko_msg, ok_msg)


def _data_check(_type, ds, spec, check_logic, fail_msg, success_msg):
    constraints = spec.get(_type, {})
    if not constraints:
        return {"status": 1, "info": ["No constraints -> Skipped"]}

    def _do_check(variable_name, expected, mandatory_constraint, out, **kwargs):
        try:
            results = check_logic(ds, variable_name, expected, **kwargs)
        except KeyError:
            return
        if results["failure"]:
            if mandatory_constraint:
                level, status = "errors", 0
            else:
                level, status = "warnings", 0
            msg = fail_msg.format(**results)
        else:
            level, status = "info", 1
            msg = success_msg.format(**results)
        out.setdefault(level, []).append(msg)
        out["status"] = status

    outcome = {"status": 1}
    for name, var_spec in constraints.get("expected", {}).items():
        try:
            mandatory = var_spec.pop("mandatory")
        except KeyError:
            mandatory = True
        if name == "default":
            for var_name, expected_value in var_spec.items():
                _do_check(var_name, expected_value, mandatory, outcome)
        else:
            try:
                nc_var = ds.variables[name]
            except KeyError:
                continue
            cell_method_condition = var_spec.get("with_cell_methods")
            if cell_method_condition is not None:
                if nc_var.cell_methods == cell_method_condition:
                    continue
            for dimension, expected_value in var_spec["dimensions"].items():
                # TODO: Do I have to check the config file at the same time? e.g:
                #  here the dim_name given in the config must be a valid dim of the
                #  specified variable
                for var_dimension in nc_var.dimensions:
                    if var_dimension == dimension:
                        _do_check(
                            name, expected_value, mandatory, outcome, dim_name=dimension
                        )
    return outcome


def _ncattr_present(value):
    return value is not None


def _simple_equality_check(actual, constraints, warning_msgs, error_msgs):
    if not constraints:
        return {"status": 1, "info": ["No constraints -> Skipped"]}
    expected = constraints["expected"]
    if actual == expected:
        outcome = {"status": 1, "info": ["OK"]}
    else:
        context = locals()
        if not constraints.get("mandatory", True):
            outcome = {
                "status": 1,
                "warnings": [m.format(**context) for m in warning_msgs],
            }
        else:
            outcome = {"status": 0, "errors": [m.format(**context) for m in error_msgs]}
    return outcome
