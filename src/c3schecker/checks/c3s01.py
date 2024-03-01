import datetime
import re
import logging
import os

import numpy as np
from c3schecker.checks import register
from netCDF4 import Dataset
import netCDF4 as nc
from numpy.ma import MaskedArray

from cfunits import Units
from xml.etree import ElementTree
from pkg_resources import resource_filename

import warnings
warnings.simplefilter(action='ignore', category=Warning)


CONVENTION = "C3S-0.1"
NUMBER_REGEX = re.compile(r"^[-+]?[0-9]+.?[0-9]*$")


# Test 1. Check the filename convention
@register(CONVENTION, "c3s_filename_convention")
def c3s_filename_convention_check(
    ds: Dataset, 
    spec: dict, 
    excep: dict, 
    verbose, operational
    ) -> dict: 
    
    outcome = {"status": 1}
    if verbose:
        logging.info("Check the C3S filename convention")

    if operational:
        if verbose:
            logging.info(
                "Operational check is the same "
                "with the non operational check!"
                )
    
    forecast_type = ds.forecast_type
    
    #lfpw_System8-v20210101_forecast_S2023030100_land_day_soil_mrlsl_r10i00p00.nc
    if forecast_type == "analysis":
        expected_filename = re.compile(
            r"^\w{4}_.+-v\d{8}_analysis_S\d{10}_\w+_\w+_\w+_\w+_r\d+i\d+p\d+.nc$"
            )
    else:
        expected_filename = re.compile(
            r"^\w{4}_.+-v\d{8}_(forecast|hindcast)_S\d{10}_\w+_\w+_\w+_\w+_r\d+i\d+p\d+.nc$"
            )
    actual_filename = os.path.basename(ds.filepath())
    check_result = re.match(expected_filename, actual_filename)


    if not check_result:
        if verbose:
            logging.error(
                f"Filename doesn't follow the filename convention {' '*10} --> NOK"
                )
            logging.error(
                f"Actual name         :  {actual_filename}"
                )
            logging.error(f"Expected filename convention  :  {expected_filename}")
            logging.error(
                "Filename example: "
                "lfpw_System8-v20210101_forecast_S2023030100_land_day_"
                "soil_mrlsl_r10i00p00.nc"
                )

        status = 0
        msg_status = "errors"
        message = [
            f"Filename doesn't follow the filename convention: Actual filename"
                    f"[{actual_filename}]. Expected: [{expected_filename}]"
                    ] 
    else: 
        if verbose:
            logging.info(
                f"Filename matches with the convention {' '*90} --> OK"
                )
            logging.info(
                f"Actual name: {str(actual_filename):<88} {' '*25} --> OK."
                )
        status = 1
        msg_status = "info"
        message = ['Filename convention OK']

    outcome["status"] = status
    outcome[msg_status] = message
    
    #print(outcome)
    return outcome

# Test 2. Check the filename of the dataset and compare with the global attributes
@register(CONVENTION, "c3s_filename_reconstruction")
def c3s_filename_reconstruction_check(
        ds: Dataset, 
        spec: dict, 
        excep: dict,  
        verbose, operational
        ) -> dict: 

    outcome = {"status": 1}
    institute_id = ds.institute_id
    system = ds.source.split()[0].split(":")[0]
    
    exceptions = excep.get(
        "exceptions", {}).get(institute_id, {}).get(system, {}).get("filename", {}
                                                                    )
    if verbose:
        logging.info(
            "Check the filename of the dataset and compare " 
            "with the global attributes"
            )
    if operational:
        if verbose:
            logging.info(
                "Operational check is the" 
                "same with the non operational check!"
                 )
    fname_elements = []      

    try:
        fname_elements.append(ds.institute_id)
        fname_elements.append(ds.source.split(':')[0])
        fname_elements.append(ds.forecast_type)
        reft = ds.forecast_reference_time
        fname_elements.append('S%s%s%s%s' % (reft[0:4],reft[5:7],reft[8:10],reft[11:13]))
        fname_elements.append(ds.modeling_realm)
        fname_elements.append(ds.frequency)
        fname_elements.append(ds.level_type)   
        vars = {}            
        for k, v in list(ds.variables.items()):
            coord_bounds_scala_var = [
                "hcrs", "lat", "lat_bnds", "lon", "lon_bnds", "plev", 
                "leadtime", "height", "sigma_theta", "temperature",
                "leadtime_bnds", "reftime", "time", "time_bnds", 
                "realization", "depth", "depth_bnds" 
                ]
            if k not in coord_bounds_scala_var:
                vars[k] = v

        fname_elements.append(list(vars.keys())[0]) 
        if ds.frequency=='fix' and ds.institute_id=='egrr':
            ripstr = 'r000i000p000'
        else:
            ripvar = ds.variables['realization'][:]
            # in python3 ripvar is an array of 'byte' characters
            # using b"" and .decode() is backwards compatible with python2
            ripstr = b"".join(
                ripvar.filled()
                ).decode() if np.ma.is_masked(ripvar) else b"".join(ripvar).strip().decode()

        fname_elements.append(ripstr)   
        fname = '_'.join(fname_elements) + '.nc'
        fname_from_file = os.path.basename(ds.filepath())

        if list(vars.keys())[0] in exceptions:
            if verbose:
                logging.warning(
                    f"Filename doesn't match with the global attributes      --> OK "
                    f"     --> Under exception"
                    )
                logging.warning(
                    f"Actual name         :  {fname_from_file}"
                    )
                logging.warning(
                    f"Reconstructed name  :  {fname}"
                    )
            status = 1
            msg_status = "warnings"
            message = [
                f"Filename doesn't match with the global attributes: Actual: "
                f"[{fname_from_file}]. Expected: [{fname}]. Under exception."
                ]     
        elif fname!=fname_from_file:
            if verbose:
                logging.error(
                    f"Filename doesn't match with the global attributes {' '*83} --> NOK"
                    )
                logging.error(f"Actual name         :  {fname_from_file}")
                logging.error(f"Reconstructed name  :  {fname}")
            status = 0
            msg_status = "errors"
            message = [
                f"Filename doesn't match with the global attributes: Actual name: "
                        f"[{fname_from_file}]. Expected name: [{fname}]"
                        ] 
        else: 
            if verbose:
                logging.info(
                    f"Filename matches with the global attributes {' '*83} --> OK"
                    )
                logging.info(
                    f"Actual name: {str(fname_from_file):<103} {' '*10} --> OK"
                    )
            status = 1
            msg_status = "info"
            message = ['Filename reconstruction OK']

    except:
        status = 0
        msg_status = "errors"
        message = ["Not enough attributes available or" 
                   "wrong attributes values to build C3S filename"]
        if verbose:
            logging.error(
                f"Not enough attributes available or wrong"
                f" attributes values to build C3S filename"
                )
            logging.error(f"The file name elements: {fname_elements}")

    outcome["status"] = status
    outcome[msg_status] = message
    
    #print(outcome)
    return outcome


# Test 3. Check only the conventions C3S-0.1 and CF-1.6
@register(CONVENTION, "c3s_metadata_convention")
def c3s_meta_convention_check(
    ds: Dataset, 
    spec: dict, 
    excep: dict, 
    verbose, operational
    ) -> dict:
    
    outcome = {}
    constraints = spec.get("convention", {})
    expected = constraints.get("expected")
    if verbose:
        logging.info("Check the conventions of the data")
    
    if operational:
        if verbose:
            logging.info(f"Operational check is the same with the non operational check!")
    
    try:
        actual = ds.Conventions
    except AttributeError:
        actual = "Absent (the dataset doesn't have a 'Conventions' attribute)"


    err_msgs = f"Global Metadata *Conventions* must be set to '{expected}'. "
    f"Currently: '{actual}'" 
    warn_msgs = f"Global Metadata *Conventions* must be set to '{expected}' "
    f"(Not Mandatory). Currently: '{actual}'"
     
    result =  _simple_equality_check(actual, constraints, warn_msgs, err_msgs)
    
    #outcome = outcome | result
    outcome = result
    
    if verbose:
        if outcome["status"] == 1:
            logging.info(f"The convention(s) are: {str(actual):<20} {' '*70} --> OK")
        else:
            logging.error(f"The convention(s) are: {str(actual):<20} {' '*70} "
                          f"--> NOK, different from the expected {expected}")

    #print(outcome)
    return outcome


# Test 4. Check the netcdf format
@register(CONVENTION, "c3s_netcdf_format")
def c3s_meta_netcdf_format_check(
    ds: Dataset, 
    spec: dict, 
    c3s_excep: dict, 
    verbose, operational
    ) -> dict:

    outcome = {}
    constraints = spec.get("netcdf_format", {})
    expected = constraints.get("expected")
    if verbose:
        logging.info("Check the format of the data")
        
    if operational:
        if verbose:
            logging.info(
                f"Operational check is the same with the non operational check!"
                )
    actual = ds.file_format
    err_msgs = f"NetCDF *file_format* must be set to '{expected}'. " 
    f"Currently: '{actual}'"
    warn_msgs = f"NetCDF *file_format* must be set to '{expected}' (Not Mandatory). "
    f"Currently: '{actual}'"
    result =  _simple_equality_check(actual, constraints, warn_msgs, err_msgs)
    outcome = outcome | result
    
    if verbose:
        if outcome["status"] == 1:
            logging.info(f"The format of the file is: {str(actual):<30} {' '*55} --> OK")
        else:
            logging.error(
                f"The format of the file is: {str(actual):<30} {' '*55} --> "
                f"NOK, different from the expected {expected}"
            )
        
    #print(outcome)
    return outcome

# Test 5. Check the number of variables in the output file
@register(CONVENTION, "c3s_scientific_variables_per_file")
def c3s_meta_number_data_var_per_file(
    ds: Dataset, 
    spec: dict, 
    excep: dict, 
    verbose, operational
    ) -> dict:
    # Data vars are scientific data discretized over a domain. The domain is defined
    # by a set of coordinate variables. Data vars therefore depend on coordinate
    # variables, so they have a coordinates attributes. And they are the only ones
    # that can have that on a netCDF files (at least one which follows CF-convention).
    # That is what's used here to check that a ds only have the specified number of
    # data variables
    
    outcome = {}
    if verbose:
        logging.info("Check that the file contains only one scientific variable.")
            
    if operational:
        if verbose:
            logging.info(f"Operational check is the same with the non operational check!")

    def _get_data_vars(dataset):
        return dataset.get_variables_by_attributes(coordinates=_ncattr_present)

    constraints = spec.get("nb_data_var_per_file", {})
    expected = constraints.get("expected")
    #actual_data_vars = ds.get_variables_by_attributes(coordinates=_ncattr_present)
    #actual = len(actual_data_vars)
    actual_data_vars = _get_data_vars(ds)
    actual = len(actual_data_vars)
    err_msgs = f"Only {expected} data variables must be contained in a single file. "
    f"Currently: '{actual}'"
    
    warn_msgs = f"{expected} data variables are expected to be contained in a single file "
    f"(Not Mandatory). Currently: '{actual}'"
     
    result = _simple_equality_check(
        actual, constraints, warn_msgs, err_msgs
    )
    outcome = outcome | result
    if verbose:
        if outcome["status"] == 1:
            logging.info(
                f"The file contains only one scientific variable:  "
                f"{str(actual_data_vars[0].standard_name):<47} {' '*30} --> OK"
                )
        else:
            logging.error(
                f"More than one data variable in a single file: Number of "
                f"variables: {len(actual_data_vars)} {' '*70} --> NOK"
                )
        
    #print(outcome)
    return outcome

# Test 6. Check the dimensions of variables in the output file
@register(CONVENTION, "c3s_dimensions")
def c3s_meta_dimensions_checks(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info("Check the dimensions of the dataset.")

    if operational:
        if verbose:
            logging.info(
                f"Operational check is the same with the non operational check!"
                )
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
    authorized_dims = constraints["authorized"]
    
    for dim in expected_dimensions:
        if dim not in actual_dimensions:
            msgs.append(msg_pattern.format(dim, actual_dimensions))

    # Only test for authorized dimensions if the actual count of dimensions exceeds
    # the count of expected mandatory dimensions
    
    #rest = set(expected_dimensions) - set(actual_dimensions)
    rest = [x for x in set(actual_dimensions) if not x in set(expected_dimensions) 
                or set(expected_dimensions).remove(x)]
    
    if rest:
        authorized_dims = constraints.get("authorized", [])
        if authorized_dims:
            #not_authorized = set(authorized_dims) - set(rest)
            not_authorized = [x for x in  set(rest) if not x in set(authorized_dims) 
                                  or set(authorized_dims).remove(x)]
            if not_authorized:
                msgs.append(
                    f"Dataset Dimensions {list(not_authorized)} are neither in the "
                    f"desirable/mandatory nor authorized dimensions ({authorized_dims})"
                )

    outcome = {}
    if warn_msgs:
        msg_status = "warnings"
        message = warn_msgs
    elif err_msgs:
        status = 0
        msg_status = "errors"
        message = err_msgs
    else:
        msg_status = "info"
        message = ["Test successful OK"]
        
    
    outcome["status"] = status
    outcome[msg_status] = message

    if verbose:
            
        if outcome["status"] == 1:        
            logging.info(
                f"The dimensions of the dataset are: "
                f"{str(actual_dimensions):<92} --> OK"
                )
        else:            
            logging.error(
                f"The dimensions of the dataset are: "
                f"{str(actual_dimensions):<15} --> NOK"
                )
            logging.error(
                f"Mandatory dimensions: {expected_dimensions}. "
                f"Authorized dimensions: {authorized_dims})"
                )
    
    #print(outcome)
    return outcome

######################
# Test 7. Check the dimensions of variables in the file
@register(CONVENTION, "c3s_dimensions_per_variable")
def c3s_meta_variable_dimensions_checks(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info("Check the dimensions of the variables.")

    if operational:
        if verbose:
            logging.info(
                f"Operational check is the same with the non operational check!"
                )
    overall_constraints = spec.get("dimensions_per_var_name", {})
    outcome = {"status": 1}
    modeling_realm = ds.modeling_realm

    for var_name, nc_var in ds.variables.items():
        var_name_constrains = var_name
        actual_dimensions = ds[var_name].dimensions
        if modeling_realm == "ocean" and var_name == "depth":
            var_name_constrains = "depth_ocean"
        elif modeling_realm == "ocean" and var_name == "depth_bnds":
            var_name_constrains = "depth_bnds_ocean"
        elif modeling_realm == "soil" and var_name == "depth":
            var_name_constrains = "depth_soil"
        
        var_specific_constraints = overall_constraints.get(var_name_constrains, {}) 
        expected_dimensions = tuple(var_specific_constraints)
        
        if actual_dimensions == expected_dimensions:
            outcome["status"] = 1
            outcome.setdefault("info", []).append(f"{var_name}: dimensions OK")
            if verbose:
                logging.info(
                    f"Variable:  {var_name:<13} with dimensions: "
                    f"{str(actual_dimensions):<92} --> OK"
                )
        else:
            outcome["status"] = 0
            error_message = [
                f"Variable '{var_name}' with wrong dimensions; "
                f"expected: {expected_dimensions}; actual: {actual_dimensions}"
            ]
            outcome["errors"] = error_message
            if verbose:
                logging.error(
                    f"Variable:  {var_name:<13} with wrong dimensions. "
                    f"Expected: {str(expected_dimensions):<35} "
                    f"Actual {str(actual_dimensions):<33} --> NOK"
                )
    #print(outcome)
    return outcome
########################

########################
# Test 8.1 Check the coordinates of the dataset and the hcrs variable.
@register(CONVENTION, "c3s_variables")
def c3s_coordinates_per_var_name(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    overall_constraints = spec.get("variables_per_var_name", {})
    if verbose:
        logging.info("Check the variables of the dataset.")
    if operational:
        if verbose:
            logging.info(
                f"Operational check is the same with the non operational check!"
                )
    
    status = 1
    outcome = {"status": status}

    actual_data_vars = _get_data_vars(ds)
    parameters_var_name = actual_data_vars[0].name
    try:
        expected_coordinates = overall_constraints[parameters_var_name]

        for coordinate in expected_coordinates:
            try:
                coords_var = ds.variables[coordinate]
                coords_name = coords_var.name
                if coords_name in expected_coordinates:
                    outcome.setdefault("info", []).append(
                        f"Variable ({coords_var.name}): OK"
                        )
                    if verbose:
                        logging.info(
                            f"Variable: {str(coords_var.name):<13} "
                            f"found in the dataset"
                            f"{' '*85} --> OK"
                        )
            except KeyError:
                outcome.setdefault("errors", []).append(
                    f"Variable ({coordinate}) is required "
                    f"for the parameter {parameters_var_name} "
                    f"but is missing"
                )
                status = 0
                if verbose:
                    logging.error(
                        f"Variable: {str(coordinate):<13} is missing "
                        f"{' '*94} --> NOK"
                    )

        actual_coordinates = []
        for var_name, nc_var in ds.variables.items():  
            if var_name == parameters_var_name or "bnds" in var_name or var_name == "hcrs":
                continue
            else:
                actual_coordinates.append(var_name)

        additional = [item for item in actual_coordinates if item not in expected_coordinates]
        
        # missing coordinates have been already detected about. We don't need another check
        #missing = [item for item in expected_coordinates if item not in actual_coordinates]
        
        if len(additional) > 0:
            for var in additional:
                # TODO: if we can describe the error/warning better. What if the coordinate is
                    # dimensionless?
                    #print(ds.variables[var].name == ds.variables[var].dimensions[0])
                # if len(ds.variables[var].dimensions) == 1:
                #     outcome.setdefault("warnings", []).append(
                #         f"Coordinate variable ('{var}') is not described in the "
                #         f"C3S guidelines. Additional coordinate variable"
                #     )
                #     if verbose:
                #         logging.warning(
                #             f"Coordinate variable ('{var}') is not described in the "
                #             f"C3S guidelines. It's an additional coordinate variable"
                #         )     
                # else:
                status = 0
                outcome.setdefault("errors", []).append(
                    f"Additional variable ('{var}') was found"
                )
                if verbose:
                    logging.error(
                        f"Additional variable ('{var}') was found {' '*91} --> NOK"
                    ) 
    except:
        status = 0
        outcome.setdefault("errors", []).append(
            f"Variable ({parameters_var_name}) is not a C3S "
            f"parameter"
        )
        if verbose:
            logging.error(
                f"Variable: ({parameters_var_name}) is not a C3S "
                f"parameter. Do not continue checking the rest of "
                f"the variables {' '*70} --> NOK"
            )

    
    outcome["status"] = status
    #print(outcome)
    return outcome
########################

########################

# Test 8. Check the attributes of of the coordinates.
@register(CONVENTION, "c3s_coordinates_attributes")
def c3s_meta_attributes_per_var_name(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    overall_constraints = spec.get("attributes_per_var_names", {})
    if verbose:
        logging.info("Check the attributes of the coordinates. ")
    if operational:
        if verbose:
            logging.info(
                f"Operational check is the same with the non operational check!"
                )
    
    institute_id = ds.institute_id
    system = ds.source.split()[0].split(":")[0]
    
    if not overall_constraints:
        return { "status": 1, "info": ["No constraints -> Skipped"]}

    outcome = {"status": 1}
    new_status = 1
    for var_name, constraints in overall_constraints.items():
        instantaneous = ds.get_variables_by_attributes(cell_methods = "leadtime: point")
        if var_name == "required" or var_name == "test":
            continue
        expected = constraints["expected"]
        if var_name == "time_accu" and instantaneous:
            continue
        if var_name == "time_inst" and not instantaneous:
            continue
        if var_name == "time_inst" or var_name == "time_accu":
            var_name = "time"
        query = {"name": var_name}
        query.update({attr: _ncattr_present for attr in expected})
        result = ds.get_variables_by_attributes(**query)        
        if len(result) == 1:
            outcome.setdefault("info", []).append(f"{var_name}: OK")
            if verbose:
                logging.info(
                    f"Variable:  {var_name:<15} with attributes: "
                    f"{str(expected):<100} --> OK"
                    )
        else:
            variable = ds.variables.get(var_name)
            level_type = getattr(ds, "level_type")

            if variable is not None:        
                #if ds.get_variables_by_attributes(cell_methods = "leadtime: point"):
                exceptions = excep.get(
                    "exceptions", {}
                    ).get(institute_id, {}).get(
                    system, {}
                    ).get("attributes_per_var_name", {}).get(
                    var_name, {}).get("expected", {}
                    )
                system_in_exception = excep.get(
                    "exceptions", {}).get(institute_id, {}
                    )
                # †hink if we want to keep that exception under general exceptions 
                # or put it specific for the origin/systems
                if set(exceptions) == set(variable.ncattrs()):
                    message_type = "warnings"
                    outcome.setdefault(
                        message_type, []).append(
                            f"{var_name}: unter exception, instantaneous variable, "
                            f"expected: {expected}; Actual: {variable.ncattrs()}"
                            )
                    if verbose:
                        logging.warning(
                            f"Variable:  {var_name:<15} with actual attributes "
                            f": {str(variable.ncattrs()):<90}   --> NOK  --> "
                            f"Unter exception (instantaneous variable)"
                            )
                        logging.warning(
                            f"Variable:  {var_name:<15} Expected attributes    "
                            f": {str(expected):<65}"
                            )
                        logging.warning(
                            f"Variable:  {var_name:<15} Exception              "
                            f": {str(exceptions):<65}"
                            )
                        for system in system_in_exception.keys():
                            logging.error(
                                f"Variable:  {var_name:<15} System under "
                                f"exception : {str(system):<80}"
                                )   
                else:
                    message_type = "errors"
                    new_status = 0
                    outcome.setdefault(
                        message_type, []).append(
                            f"{var_name}: wrong mandatory attributes, "
                            f"expected: {expected}; Actual: {variable.ncattrs()}"
                            )
                    if verbose:
                        logging.error(
                            f"Variable:  {var_name:<15} with wrong attributes"
                            f"{' '*96} --> NOK"
                            )
                        logging.error(
                            f"Variable:  {var_name:<15} actual attributes "
                            f": {str(variable.ncattrs()):<90}"
                            )
                        logging.error(
                            f"Variable:  {var_name:<15} expected attributes    "
                            f": {str(expected):<65}"
                            )
            outcome["status"] = outcome["status"] and new_status
                
    #print(outcome)
    return outcome



# Test 9. Check the calendar attributes of time coordinates.
@register(CONVENTION, "c3s_calendar")
def c3s_meta_attributes_possible_values(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info(
            "Check the calendar attribute of the coordinates 'time' and 'reftime'."
            )
        
    if operational:
        if verbose:
            logging.info(
                f"Operational check is the same with the non operational check!"
                )

    overall_constraints = spec.get("possible_values_per_attributes", {})
    outcome = {"status": 1}

    for attr_name, constraints in overall_constraints.items():
        query = {attr_name: _ncattr_present}
        vars_with_attr = ds.get_variables_by_attributes(**query)
        if attr_name == "required" or attr_name == "test":
            continue
        possible_values = constraints["expected"]
        for variable in vars_with_attr:
            actual_value = getattr(variable, attr_name)
            if actual_value in possible_values:
                outcome.setdefault("info", []).append(
                    f"{variable.name} {attr_name}: OK"
                )
                if verbose:
                    logging.info(
                        f"Variable {(variable.name):<13} "
                        f"with attribute: {attr_name} "
                        f"and value {actual_value} {' '*59} --> OK"
                        )
            else:
                message_type = "errors"
                new_status = 0
                outcome.setdefault(message_type, []).append(
                    f"Attribute '{attr_name}' value for '{variable.name}'"
                    f"({actual_value}) is not allowed. "
                    f"Possible values: {possible_values}"
                )
                if verbose:
                    logging.error(f"Variable {(variable.name):<12} "
                                  f"with attribute: {attr_name} "
                                  f"and value {actual_value} {' '*59}  --> NOK. "
                                  f"Requered: {possible_values}")
                

                outcome["status"] = outcome["status"] and new_status  
    #print(outcome)
    return outcome

# Test 10. Check the values of the attributes for all the variables
@register(CONVENTION, "c3s_exact_attributes_values")
def c3s_meta_attributes_exact_values_per_var_name(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info("Check the values of the attributes for all the variables.")
    if operational:
        if verbose:
            logging.info(
                f"Operational check is the same with the non operational check!"
                )
    overall_constraints = spec.get("attributes_values_per_var_name", {})
    outcome = {"status": 1}
    # Some of the attribute values should be checked against a regular expression
    check_regex = ["cell_methods"]
    institute_id = ds.institute_id
    system = ds.source.split()[0].split(":")[0]

    for var_name, nc_var in ds.variables.items():
        var_specific_constraints = overall_constraints.get(var_name, {}) 
        var_attrs = []
        
        #global_attrs = []
        for global_attr_name, expected_value in var_specific_constraints.get(
            "global", {}
        ).items(): 
            actual_global_value = ds.getncattr(global_attr_name)
        
            if actual_global_value == expected_value:
                outcome.setdefault("info", []).append(
                    f"{var_name} {global_attr_name}: OK"
                    )
                if verbose:
                    logging.info(
                        f"Variable: {var_name:<12} global attribute: {global_attr_name:<17} "
                        f"value: {actual_global_value:<53} --> OK"
                    )
        
        actual_data_vars = _get_data_vars(ds)
        scientific_var_name = actual_data_vars[0].name
        
        for attr_name, expected_value in var_specific_constraints.get(
            "expected", {}
        ).items(): 
            var_attrs.append(attr_name)

        for attr_name, expected_value in var_specific_constraints.get(
            "expected", {}
        ).items():
            
            if (scientific_var_name == "uas"
                or scientific_var_name == "vas"
                or scientific_var_name == "wsgmax"
                ):
                if attr_name == "valid_max":
                    expected_value = 30.0
            
            if attr_name in nc_var.ncattrs():
                pass
                # if verbose:
                #     logging.info(
                #         f"Variable:  {var_name:<12} Number of attributes "
                #         f"as requested."
                #         )
            else:
                if len(nc_var.ncattrs()) > len(var_attrs):
                    if verbose:
                        logging.warning(
                            f"Variable: {var_name:<12} Additional attributes "
                            f"were found."
                        )
                        logging.error(
                            f"Variable: {var_name:<12} Actual attribute: "
                            f"{nc_var.ncattrs()} Expected attributes: "
                            f"{var_attrs}"
                        )
            try:
                actual_value = str(nc_var.getncattr(attr_name))
                
                ## Does the actual value look like a number?
                #if NUMBER_REGEX.match(actual_value):
                ##    # If yes, convert it to the type of the referring var
                #    actual_value = np.array(
                #        nc_var.getncattr(attr_name), dtype=nc_var.dtype
                #    )
            except AttributeError:
                exceptions = excep.get(
                    "exceptions", {}).get(institute_id, {}).get(
                        system, {}).get("attributes_values_per_var_name", {}).get(
                        var_name, {}).get("expected", {})
                exception = False
                for attr, value in exceptions.items():
                    exception = False
                    if attr_name not in attr:
                        exception = True
                if exception:
                    outcome.setdefault("warnings", []).append(
                        f"Variable {var_name}' is missing attribute "
                        f"'{attr_name}'. OK Unter exception'"
                        )
                    outcome["status"] = 1
                    if verbose:
                        logging.warning(
                            f"Variable: {var_name:<12} attribute {' '*6}: "
                            f"{attr_name:<10} --> OK (missing, as an exception)"
                            )
                        logging.warning(
                            f"Variable: {var_name:<12} attribute {' '*6}: "
                            f"{attr_name:<10} --> The exception is {exceptions}."
                            )
                    continue
                else:
                    outcome.setdefault("errors", []).append(
                        f"Variable '{var_name}' is missing attribute '{attr_name}'"
                        )
                    outcome["status"] = 0
                    if verbose:
                        logging.error(
                            f"Variable: {var_name:<12} attribute {' '*6}: "
                            f"{attr_name:<30} {' '*48}--> NOK (Attribute '{attr_name}' "
                            f"not found)"
                            )
                    continue
            
            
            actual_value = str(actual_value)
            expected_value = str(expected_value)
            check_result = actual_value == expected_value

            if attr_name not in check_regex:
                #if NUMBER_REGEX.match(str(expected_value)):
                #    expected_value = np.array(expected_value, dtype=nc_var.dtype)
                check_result = actual_value == expected_value
            else:
                
                check_result = re.match(expected_value, actual_value)
            if check_result and attr_name not in "cell_methods":
                #interval = re.findall('interval:.+', actual_value)
                outcome.setdefault("info", []).append(f"{var_name} {attr_name}: OK")
                if verbose:
                    logging.info(
                        f"Variable: {var_name:<12} attribute {' '*6}: {attr_name:<17} "
                        f"value: {actual_value:<53} --> OK"
                    )
            elif check_result and attr_name == "cell_methods":
                if "point" not in actual_value:
                    outcome.setdefault("warnings", []).append(
                        f"Variable: '{var_name}', attribute: '{attr_name}', actual value '{actual_value}' "
                        f"manual inspection: the interval is required to have a value<=3 hours"
                    )
                    if verbose:
                        logging.info(
                                f"Variable: {var_name:<12} attribute {' '*6}: {attr_name:<17} "
                                f"value: {actual_value:<53} --> OK (cell_methods attributes is compliant to the regex)"
                            )
                        logging.warning(
                            f"Variable: {var_name:<12} attribute {' '*6}: "
                            f"{attr_name:<17} "
                            f"Manual inspection of the interval. "
                            f"The interval is required to have a value<=3 hours)"
                        )
                        logging.info(
                            f"Variable: {var_name:<12} attribute {' '*6}: {attr_name:<17} "
                            f"value: {actual_value:<53} (value<=3 hours)"
                        )
                else:
                    outcome.setdefault("info", []).append(f"{var_name} {attr_name}: OK")
                    if verbose:
                        logging.info(
                            f"Variable: {var_name:<12} attribute {' '*6}: {attr_name:<17} "
                            f"value: {actual_value:<53} --> OK"
                        )

            else:
                try:
                    exceptions = excep.get("exceptions", {}).get(
                        institute_id, {}).get(system, {}).get(
                            "attributes_values_per_var_name", {}).get(
                                var_name, {}).get("expected", {})
                    if str(nc_var.getncattr(attr_name)) not in str(exceptions.get(attr_name)):
                        message_type = "errors"
                        new_status = 0
                        outcome.setdefault(message_type, []).append(
                            f"Attribute '{attr_name}' of variable '{var_name}' "
                            f"({actual_value}) is not allowed. Expected: {expected_value}"
                            )
                        
                        if verbose:
                            logging.error(
                                f"Variable: {var_name:<12} "
                                f"attribute {' '*6}: {attr_name:<17} value: "
                                f"{actual_value:<53} --> "
                                f"NOK (wrong attribute value; expected value: "
                                f"({expected_value})"
                                )
                        if attr_name in "valid_min" or attr_name in "valid_max":
                            if not isinstance(
                                nc_var.getncattr(attr_name), np.float32
                                ) or not isinstance(
                                    nc_var.getncattr(attr_name), np.float64
                                ):
                                if verbose:
                                    logging.error(
                                        f"Variable: {var_name:<12} "
                                        f"attribute {' '*6}: {attr_name:<17} value: "
                                        f"{actual_value:<53} --> "
                                        f"NOK (expected dtype: float; actual:"
                                        f"({type(nc_var.getncattr(attr_name))}))"
                                    )
                    else:
                        message_type = "warnings"
                        new_status = 1
                        if verbose:
                            logging.warning(
                                f"Variable:  {var_name:<12} attribute {' '*6}: {attr_name:<17} "
                                f"--> OK (as an exception). Expected value: ({expected_value}), "
                                f"Actual value: ({nc_var.getncattr(attr_name)})"
                                )
                        outcome.setdefault(message_type, []).append(
                            f"Attribute '{attr_name}' of variable '{var_name}' "
                            f"({actual_value}) is allowed as an exception."
                            )
                except AttributeError:
                    if verbose:
                        logging.error(
                            f"Variable:  {var_name:<12} attribute {' '*6}: {attr_name:<17} --> "
                            f"NOK (values is not allowed)."
                            f" Expected value: ({expected_value}), "
                            f"Actual value: ({nc_var.getncattr(attr_name)})"
                            )
                    message_type = "errors"
                    new_status = 0
                    outcome.setdefault(message_type, []).append(
                        f"Attribute '{attr_name}' of variable '{var_name}' ({actual_value})"
                        f" is not allowed. Expected: {expected_value}"
                        )
                    
                outcome["status"] = outcome["status"] and new_status
    
    #print(outcome)
    return outcome

# Test 11. Check the global attributes of the dataset. 
@register(CONVENTION, "c3s_global_attributes")
def c3s_meta_global_attributes(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info("Check the global attributes of the dataset.")
    if operational:
        if verbose:
            logging.info(
                "For operational check all the expected "
                "global attributes are mandatory."
                )
    constraints = spec.get("global_attributes", {})
    outcome = {"status": 1}
    
    if not constraints:
        return {"status": 1, "info": ["No constraints -> Skipped"]}
    actual = set(sorted(ds.ncattrs()))
    expected = set(sorted(constraints["expected"]))
    missing = expected - actual
    additional = actual - expected
    if not missing and not additional:
        outcome = {
            "status": 1, "info": 
            ["OK, no global attribute is missing, "
            "no additional global attributes"]
            }
        if verbose:
            logging.info(f"Global attributes {' '*60} --> OK")
    
    for attribute in (list(actual)):
        outcome.setdefault("info", []).append(
            f"Global Attribute '{attribute}' OK"
        )
        if verbose:
            required = str(constraints.get(
                "expected").get(attribute, {}).get("required", {})
                )
            logging.info(
                f"Global attribute:  {attribute:<25} --> OK "
                f" |  ({required:<9} attribute)"
                )
    status = 1
    if missing:
        for global_attribute in missing: 
            required_attr = constraints["expected"].get(global_attribute)
            if required_attr.get("required") == 'mandatory':
                level = "errors"
                status = 0
                outcome.setdefault(level, []).append(
                    f"Global Attribute '{global_attribute}' "
                    f"is missing and it's a {required_attr.get('required')}"
                    )
                if verbose:
                    logging.error(
                        f"Global Attribute:  {global_attribute:<20} is missing "
                        f"and it's a {required_attr.get('required')}"
                        )
            else:
                if operational:
                    level = "errors"
                    outcome.setdefault(level, []).append(
                        f"Global Attribute '{global_attribute}' is missing (required: "
                        f"{required_attr.get('required')}). Operational mode: "
                        f"All the global attributes are mandatory "
                        )
                    if verbose:
                        logging.error(
                            f"Global Attribute:  {global_attribute:<25} --> NOK |  missing "
                            f"(required: {required_attr.get('required')}). Operational mode: "
                            f"All the global attributes are mandatory "
                            )
                else:
                    level = "warnings"
                    outcome.setdefault(level, []).append(
                        f"Global Attribute '{global_attribute}' "
                        f"is missing but it's a {required_attr.get('required')}"
                        )
                    if verbose:
                        logging.warning(
                            f"Global Attribute:  {global_attribute:<25} --> OK  |  missing "
                            f"({required_attr.get('required')}, non operational mode)"
                            )

    if additional:
        if verbose:
            logging.warning(f"Additional global attribute(s):   [{additional}] ")
        for global_attribute in additional:
            level = "warnings"
            outcome.setdefault(
                level, []).append(
                    f"Global Attribute '{global_attribute}' "
                    f"is an additional attribute"
                    )
            if verbose:
                logging.warning(
                    f"Global Attribute:  {global_attribute:<20} is an "
                    f"additional to the C3S global attribute")
    
    outcome["status"] = status
    #print(outcome)
    return outcome

# Test 12. Check the values of the global attributes.
@register(CONVENTION, "c3s_global_attributes_values")
def c3s_meta_global_attributes_possible_values(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info("Check the values of the global attributes.")
    if operational:
        if verbose:
            logging.info(
                "Values of optional attributes follow CV only in operational mode"
                )
    constraints = spec.get("global_attributes_possible_values", {})
    status = 1
    outcome = {"status": status}
    if not constraints:
        return {"status": 1, "info": ["No constraints -> Skipped"]}
    actual = set(sorted(ds.ncattrs()))
    for attribute in actual:
        if constraints.get("expected").get(attribute):
            possible_values = constraints.get("expected").get(attribute).get("value")
        else:                
            possible_values = constraints.get("expected").get(attribute)
        
        actual_value = getattr(ds, attribute)
        if actual and possible_values:
            required = str(constraints.get(
                "expected").get(attribute, {}).get("required", {})
                )
            if actual_value in possible_values:
                outcome.setdefault("info", []).append(
                    f"{attribute} follows the "
                    f"Controlled Vocabulary, ({required} attribute)"
                    )
                if verbose:
                    logging.info(
                        f"The attribute:  {attribute:<20} follows the Controlled Vocabulary "
                        f"--> OK  |  ({required:<9} attribute)"
                    )
            else:
                if required in "mandatory":
                    status = 0
                    outcome.setdefault("errors", []).append(
                        f"{attribute}: doens't follow the Controlled "
                        f"Vocabulary and it's '{required}' attribute. " 
                        f"Possible values for: {attribute}: "
                        f"{possible_values} but actual value is {actual_value} "
                        )
                    if verbose:
                        logging.error(
                            f"The attribute: {attribute:<20} doens't follow the Controlled "
                            f"Vocabulary and it's '{required}' attribute. Possible values: "
                            f"{possible_values}, actual value is '{actual_value}'"
                            )
                else:
                    if operational:
                        outcome.setdefault("errors", []).append(
                            f"{attribute}: doens't follow the Controlled Vocabulary "
                            f"('{required}' attribute, operational mode) " 
                            f"Possible values for {attribute}: "
                            f"{possible_values} but actual value is {actual_value} ")
                        if verbose:
                            logging.error(
                                f"The attribute:  {attribute:<20} doesn't follow "
                                f"the Controlled Vocabulary ('{required}' attribute, "
                                f"operational mode). Possible values: {possible_values}  "
                                f"Actual value: '{actual_value}'"
                                )
                    else:
                        outcome.setdefault("warnings", []).append(
                            f"{attribute}: doesn't follow the Controlled "
                            f"Vocabulary, but it's '{required}' attribute " 
                            f"Possible values for {attribute}: "
                            f"{possible_values} but actual value is {actual_value} "
                            )
                        if verbose:
                            logging.warning(
                                f"The attribute:  {attribute:<20} doesn't follow the "
                                f"Controlled Vocabulary ('{required}' attribute, "
                                f"non operational mode). Possible values: "
                                f"{possible_values}  Actual value is '{actual_value}'"
                                )

        if actual and not possible_values:
            outcome.setdefault("info", []).append(
                f"{attribute}: without a controlled vocabulary OK"
                )
    outcome["status"] = status
    #print(outcome)
    return outcome

# Test 13. Check the global date attribute if follows the required date format
@register(CONVENTION, "c3s_global_date_attributes_format")
def c3s_meta_global_attributes_date_format(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info(
            "Check the global date attribute if follows the required date format"
            )
    if operational:
        if verbose:
            logging.info(
                f"Operational check is the same with the non operational check!"
                )
            
    constraints = spec.get("global_attributes_date_format", {})
    required = constraints.get("required")
    
    if not constraints:
        return {"status": 1, "info": ["No constraints -> Skipped"]}
    outcome = {"status": 1}
    mandatory_constraints = constraints.get("mandatory", True)
    for date_attr_name, expected_date_attr_format in constraints["expected"].items():
        try:
            actual_date_attr_value = ds.getncattr(date_attr_name)
        except AttributeError:
            if mandatory_constraints:
                level = "errors"
                status = 0
                if verbose:
                    logging.error(
                        f"Dataset is missing global attribute: '{date_attr_name}'."
                        )
            else:
                level = "warnings"
                status = 1
            outcome.setdefault(level, []).append(
                f"Dataset is missing global attribute '{date_attr_name}'"
            )
            outcome["status"] = status
            continue
        try:
            datetime.datetime.strptime(
                actual_date_attr_value[:19], expected_date_attr_format
            )
            status = 1
            outcome.setdefault("info", []).append(f"{date_attr_name}: OK")
            if verbose:
                logging.info(
                    f"The date attribute:  {date_attr_name:<25}  with date format "
                    f"{actual_date_attr_value[:19]:<20} --> OK expected "
                    f"date format {expected_date_attr_format} "
                    )
        except ValueError:
            if mandatory_constraints:
                status = 0
                level = "errors"
                if verbose:
                    logging.info(
                        f"The date attribute:  {date_attr_name:<25}  with date format "
                        f"{actual_date_attr_value[:19]:<20} --> NOK  expected "
                        f"date format {expected_date_attr_format} "
                        )
            else:
                status = 0
                level = "warnings"
            outcome.setdefault(level, []).append(
                f"Global date Attribute '{date_attr_name}' value does not follow "
                f"required date format ({expected_date_attr_format})"
            )
        outcome["status"] = status
    #print(outcome)
    return outcome

# Test 14. Check the dimensions of the variables.
@register(CONVENTION, "c3s_variables_exact_dimensions")
def c3s_meta_variables_exact_dimensions(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info("Check the dimensions of the variables.")
        
    if operational:
        if verbose:
            logging.info(f"Operational check is the same with the non operational check!")

    constraints = spec.get("variables_exact_dimensions", {})
    required = constraints.get("required")
    if not constraints:
        return {"status": 1, "info": ["No constraints -> Skipped"]}
    outcome = {"status": 1}
    mandatory_constraints = constraints.get("mandatory", True)
    for var_name, expected_dimensions in constraints["expected"].items():
        try:
            actual_dimensions = set(ds.variables[var_name].dimensions)
        except KeyError:
            continue
        if actual_dimensions:    # To be check again the if condition here. What if the actual is empty and it's an error
            missing_dimensions = set(expected_dimensions) - actual_dimensions
        if missing_dimensions:
            if mandatory_constraints:
                status = 0
                level = "errors"
            else:
                status = 1
                level = "warnings"
            msg = (
                f"Missing dimensions {list(missing_dimensions)} for variable "
                f"'{var_name}'. Expected: {expected_dimensions}"
            )
            if verbose and status == 0:
                logging.error(
                    f"Variable:  {var_name:<12} with dimensions {actual_dimensions} "
                    f"--> NOK expected {expected_dimensions}"
                    )
            else:
                logging.warning(
                    f"Variable:  {var_name:<12} with dimensions {actual_dimensions} "
                    f"--> OK expected {expected_dimensions}"
                    )
        else:
            status = 1
            level = "info"
            msg = f"{var_name}: OK"
            if verbose:
                logging.info(
                    f"Variable:  {var_name:<12} with dimensions "
                    f"{str(actual_dimensions):<40} --> OK"
                    )

        outcome.setdefault(level, []).append(msg)
        outcome["status"] = status
    #print(outcome)
    return outcome

# TODO: The test should be removed?
# Test 15. 
@register(CONVENTION, "c3s_grib_consistency")
def c3s_meta_grib_consistency(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    constraints = spec.get("grib_consistency", {})
    if not constraints:
        return {"status": 1, "info": ["No constraints -> Skipped"]}
    outcome = {"status": 1}
    mandatory_constraints = constraints.get("mandatory", True)
    for mars_paramid, expected_bindings in constraints["expected"].items():
        query = {"mars_paramid": mars_paramid}
        nc_var = ds.get_variables_by_attributes(**query)
        if nc_var:
            nc_var = nc_var[0]
            mars_param_name = expected_bindings["name"]
            for attr_name, expected in expected_bindings["cf"].items():
                try:
                    actual_value = nc_var.getncattr(attr_name)
                except AttributeError:
                    if mandatory_constraints:
                        level = "errors"
                        status = 0
                    else:
                        level = "warnings"
                        status = 1
                    outcome.setdefault(level, []).append(
                        f"Dataset Variable {nc_var.name} is missing attribute "
                        f"'{attr_name}'"
                    )
                    if verbose:
                        logging.error(
                            f"Dataset Variable:  {nc_var.name} is missing attribute "
                            f"'{attr_name}' --> NOK"
                        )
                    outcome["status"] = status
                    continue
                if actual_value == expected:
                    status = 1
                    msg = f"mars id {mars_paramid}: OK"
                    level = "info"
                    if verbose:
                        logging.info(
                            f"MARS id {mars_paramid}, "
                            f"Attribute name:'{attr_name}' --> OK"
                        )
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
                    if verbose:
                        logging.info(f"{msg} --> NOK")
                outcome["status"] = status
                outcome.setdefault(level, []).append(msg)
    #print(outcome)
    return outcome

# Test 16. Check data intervals of the variables.
@register(CONVENTION, "c3s_data_intervals")
def c3s_data_intervals(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info("Check data intervals of the variables.")
    constraints = spec.get("data_intervals")
    status = 1
    outcome = {"status": status }        
    
    for name, var_spec in constraints.get("expected", {}).items():
        if name == "default":
            continue
        try:
            nc_var = ds.variables[name]
        except KeyError:
            continue
        #cell_method_condition = var_spec.get("with_cell_methods")
        for dimension, expected_value in var_spec["dimensions"].items():
            # TODO: Do I have to check the config file at the same time? e.g:
            #  here the dim_name given in the config must be a valid dim of the
            #  specified variable
            for var_dimension in nc_var.dimensions:
                if var_dimension == dimension:                        
                    dim_values = ds.variables[var_dimension]
                    all_intervals = dim_values[1:] - dim_values[:-1]
                    not_matching_intervals = all_intervals[
                        np.asarray(all_intervals != expected_value).nonzero()
                        ]
                    not_matching_intervals_ = all_intervals[
                        np.asarray(all_intervals != expected_value*24).nonzero()
                        ]
                    if len(not_matching_intervals) == 0 or len(not_matching_intervals_) == 0:
                        failure = False
                    else:
                        failure = True
                        
                    if len(all_intervals) == 0:
                        bad_intervals = 'no data'
                        failure = True
                    elif len(not_matching_intervals) == 0:
                        bad_intervals = list(not_matching_intervals)
                    elif len(not_matching_intervals_) == 0:
                        bad_intervals = list(not_matching_intervals_)

                    results = {
                            "var_name": name,
                            "dim_name": dim_values.dimensions,
                            "valid": expected_value,
                            "units": dim_values.units,
                            "bad_intervals": bad_intervals,
                            "failure": failure,
                            "operational_check": operational
                    }   
                    
                    try:
                        actual_value = all_intervals[0]
                    except:
                        actual_value = all_intervals
                        level, status = "errors", 0

                    if not results["failure"]:
                        level, status = "info", 1
                        msg = (
                            f"{name} (dimension {dim_values.dimensions}): "
                            f" interval is OK -> "
                            f"{actual_value} {dim_values.units}"
                            )
                        if verbose:
                            logging.info(
                                f"Variable:  {name:<12} with dimension "
                                f"{str(dim_values.dimensions):<20} "
                                f"--> OK --> Interval: "
                                f"{actual_value:<4} ({dim_values.units})"
                                )
                    else:
                        if results["operational_check"]:
                            level, status = "errors", 0
                            msg = (
                                f"Not matching intervals found for '{name}' "
                                f"dimension '{dim_values.dimensions}' "
                                f"(expected interval: {expected_value} or "
                                f"{expected_value*24} {dim_values.units}): "
                                f"{bad_intervals}")
                            if verbose:
                                logging.error(
                                    f"Variable:  {name:<12} with dimension "
                                    f"{str(dim_values.dimensions):<20} "
                                    f"--> NOK, not matching intervals found, "
                                    f"operational mode --> Actual interval: "
                                    f"{expected_value:<4} {dim_values.units}")
                        else:
                            if bad_intervals == 'no data':
                                level, status = "errors", 0
                            else:
                                level, status = "warning", 1
                            msg = (
                                f"Not matching intervals found for '{name}' dimension "
                                f"'{dim_values.dimensions}' (expected interval: "
                                f"{expected_value} or {expected_value*24} "
                                f" {dim_values.units}): {bad_intervals}. "
                                f"Non operational mode.")
                            if verbose:
                                if level == "errors":
                                    logging.error(
                                        f"Variable:  {name:<12} with dimension "
                                        f"{str(dim_values.dimensions):<20} --> "
                                        f"NOK, no intervals found, probably "
                                        f"missing data, non operational mode "
                                        f"--> Actual interval: {expected_value:<4} "
                                        f"{dim_values.units}")
                                else:
                                    logging.warning(
                                        f"Variable:  {name:<12} with dimension "
                                        f"{str(dim_values.dimensions):<20} --> "
                                        f"NOK, not matching intervals found, "
                                        f"non operational mode "
                                        f"--> Actual interval: {expected_value:<4} {dim_values.units}")
                    outcome.setdefault(level, []).append(msg)

    outcome["status"] = status
    #print(outcome)
    return outcome
    
# Test 17. Check for the min and max of the values.
@register(CONVENTION, "c3s_data_min_max")
def c3s_data_min_max(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info("Check for the min and max of the values")
    constraints = spec.get("data_min_max").get("expected")
    status = 1
    outcome = {"status": status }
    for name, var_spec in constraints.get("default", {}).items():
        try:
            dim_values = ds.variables[name][:]
            expected_min, expected_max = var_spec
            actual_min, actual_max = dim_values.min(), dim_values.max()
            results = {
                "var_name": name,
                "dim_name": name,
                "actual_min": actual_min,
                "actual_max": actual_max,
                "valid_min": expected_min,
                "valid_max": expected_max,
                "failure": (actual_min != expected_min or actual_max != expected_max),
            }
        except KeyError:
            continue
        if not results["failure"]:
            level = "info"
            msg = (
                f"{name} (dimension {name}): Mix and Max values as expected. OK -> "
                f"min={actual_min}, max={actual_max}"
                )
            outcome.setdefault(level, []).append(msg)
            if verbose:
                logging.info(
                    f"Variable:  {name:<12} with dimension {name:<12}: "
                    f"Mix and Max values as expected --> OK --> min={actual_min:<7} , "
                    f"max={actual_max:<7}")
        else:
            level, status = "errors", 0
            msg = (
                f"Invalid min/max found for '{name}' dimension '{name}' "
                f"(Actual: min={actual_min}, "
                f"max={actual_max}). Expected: min={expected_min}, max={expected_max}")
            outcome.setdefault(level, []).append(msg)
            if verbose:
                logging.info(
                    f"Variable:  {name:<12} with dimension {name:<12}: "
                    f"Invalid min/max found --> NOK --> (Actual: min={actual_min:<7} , "
                    f"max={actual_max:<7}) Expected: min={expected_min:<5}, "
                    f"max={expected_max:<5}"
                    )
                
        outcome["status"] = status

    #print(outcome)
    return outcome

# Test 18. Check data min and data max of the bounds.
@register(CONVENTION, "c3s_data_ranges")
def c3s_data_ranges(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info("Check data min and data max of the bounds")
    constraints = spec.get("data_ranges").get("expected")
    status = 1
    outcome = {"status": status }

    for name, var_spec in constraints.get("default", {}).items():
        try:
            values = ds.variables[name][:]
            bottom, top = var_spec
            if isinstance(values, MaskedArray):
                # We don't want masked values to pollute our 
                # conformity test, why we need that, is it by default the values not masked?
                values = values[~values.mask]
            out_of_range = values[np.logical_or(values < bottom, values > top).nonzero()]
            results = {
                "var_name": name,
                "dim_name": name,
                "bottom": bottom,
                "top": top,
                "out_of_range": list(out_of_range),
                "failure": out_of_range.any(),
            }
        except KeyError:
            continue
        if not results["failure"]:
            level = "info"
            msg = (
                f"{name} (dimension {name}): "
                f"Boundaries as expected. OK -> "
                f"bottom>={bottom}, top<={top}"
                )
            if verbose:
                logging.info(
                    f"Variable:  {name:<12} with dimension {name:<12}: Boundaries as "
                    f"expected --> OK --> bottom>={bottom:<6} , top<={top:<6}"
                    )
        else:
            level, status = "errors", 0
            msg = (
                f"Data out of valid range found for "
                f"'{name}' dimension '{name}':  {out_of_range}. "
                f"Expected Range: [{bottom}, {top}]")
            if verbose:
                logging.info(
                    f"Variable:  {name:<12} with dimension "
                    f"{name:<12}: Data out of valid range "
                    f"--> NOK --> Out of range: {out_of_range}. "
                    f"Expected Range: [bottom>={bottom:<6}, top<={top:<6}]")
        outcome.setdefault(level, []).append(msg)
        outcome["status"] = status
    
    #print(outcome)
    return outcome

# Test 19. Check data min and data max of the bounds.
@register(CONVENTION, "c3s_data_values")
def c3s_data_values(
    ds: Dataset, 
    spec: dict,
    excep: dict, 
    verbose, operational
    ) -> dict:
    if verbose:
        logging.info("Check for the values")
    if operational:
        if verbose:
            logging.info(
                f"Operational check is the same with the non operational check!"
                )    
    constraints = spec.get("data_values").get("expected")
    status = 1
    outcome = {"status": status }
    #def _get_data_vars(dataset):
    #    return dataset.get_variables_by_attributes(coordinates=_ncattr_present)
    
    actual_data_vars = _get_data_vars(ds)
    scientific_var_name = actual_data_vars[0].name
        
    for name, var_spec in constraints.get("default", {}).items():
        try:
            
            if "height_" in name:
                if (scientific_var_name == "uas" 
                    or scientific_var_name == "vas"
                    or scientific_var_name == "wsgmax"):
                    if name == "height_2m":
                        continue
                elif (scientific_var_name == "tas" 
                      or scientific_var_name == "tasmax"
                      or scientific_var_name == "tasmin"
                      or scientific_var_name == "tdps" 
                    ):
                    if name == "height_10m":
                        continue
                name = "height"
           
            # Unroll the expected arrays to do comparisons on 1-D arrays
            expected = np.array(var_spec).ravel()
            values = ds.variables[name][:]
            if isinstance(values, MaskedArray):
                # For masked arrays, return the non masked data as unrolled numpy array
                values = values.compressed().ravel()
            # If expected has lower nb of values than actual, pad the smaller array in all
            # possible ways in order to do comparisons: left, right, left and right
            nb_actual_values = values.shape[0]        # values.shape[0] == len(values)
            nb_expected_values = expected.shape[0]

        except KeyError:
            continue            

        var_name = name
        dim_name = name

        if nb_actual_values > nb_expected_values:
            # This gives a guarantee that we will get at most len(expected) indices,
            # which enables us to index both the expected and the values arrays
            # Get the indices of expected where the value appears in the actual array
            expected_idx_in_actual = np.flatnonzero(np.isin(expected, values))

            # Compare the expected values that are in the actual array with the
            # values of the actual arrays that are at these indices: if the 2 are
            # equal, then the expected values appear in the actual array exactly
            # as expected
            expected_is_in_order = np.all(
                expected[expected_idx_in_actual] == values[expected_idx_in_actual]
                )

            # When all expected values are there, it's not a failure
            if expected_idx_in_actual.size == nb_expected_values:
                # TODO: Should we consider the order of the expected values?
                # For now, fail if we have the expected values but they are not in order
                if expected_is_in_order:
                    results = {
                        "var_name": var_name,
                        "dim_name": dim_name,
                        "valid_values": expected,
                        "invalid_values": list(
                            values[np.isin(values, expected, invert=True)]
                        ),
                        "failure": False,
                        "warnings": True,
                    }
                    
                    invalid_values = list(values[np.isin(values, expected, invert=True)])
                    valid_values = expected
                else:
                    # In this case, there is the possibility that the values are in
                    # order, but with some additional values in between. For example:
                    # expected = [1, 2, 3]; actual = [0, 1, 1.5, 2, 3]
                    # TODO: Should we fail in this case? For now let's say no, and give
                    #   warnings
                    if np.all(values[np.isin(values, expected)] == expected):
                        results = {
                            "var_name": var_name,
                            "dim_name": dim_name,
                            "valid_values": expected,
                            "invalid_values": list(values),
                            "failure": False,
                            "warnings": True,
                        }
                        invalid_values = list(values)
                        valid_values = expected
                    else:
                        # This means the data in the actual array are completely mixed
                        # up, which we consider as an error
                        results = {
                            "var_name": var_name,
                            "dim_name": dim_name,
                            "valid_values": expected,
                            "invalid_values": list(values),
                            "failure": True,
                        }
                        invalid_values = list(values)
                        valid_values = expected
            else:
                # It's an error to not have all the expected values
                results = {
                    "var_name": var_name,
                    "dim_name": dim_name,
                    "valid_values": expected,
                    "invalid_values": list(values),
                    "failure": True,
                }
                invalid_values = list(values)
                valid_values = expected
        elif nb_actual_values < nb_expected_values:
            # It's an error to not have all the expected values
            results = {
                "var_name": var_name,
                "dim_name": dim_name,
                "valid_values": expected,
                "invalid_values": list(values),
                "failure": True,
            }
            invalid_values = list(values)
            valid_values = expected
        # If the expected and the actual are the same length
        else:
            # In this case, all values in actual array must match the expected,
            # in the same order
            if np.all(values == expected):
                results = {"var_name": var_name,
                        "dim_name": dim_name, 
                        "failure": False
                        }
            else:
                results = {
                    "var_name": var_name,
                    "dim_name": dim_name,
                    "valid_values": expected,
                    "invalid_values": list(
                        values[np.isin(values, expected, invert=True)]
                    ),
                    "failure": True,
                }
                invalid_values = list(values[np.isin(values, expected, invert=True)])
                valid_values = expected
    
        if not results["failure"]:
            level = "info"
            msg = (f"{name}: Values as expected. OK.")
            if verbose:
                logging.info(
                    f"Variable: {name:<12} "
                    f"Values as expected {' '*40} --> OK"
                )
        else:
            if not list(values[np.isin(values, expected, invert=True)]):
                institute_id = ds.institute_id
                system = ds.source.split()[0][:-1]
                exceptions = excep.get("exceptions", {}).get(
                    institute_id, {}).get(system, {}).get(
                        "data_values", {}).get(var_name, {}
                                               )
                if exceptions == list(values):
                    level, status = "warnings", 1
                    msg = (
                        f"Invalid order found for '{name}':  "
                        f"It's under exception."
                    )
                    if verbose:
                        logging.warning(
                            f"Variable: {name:<12} {' '*49} --> OK "
                            f"Invalid order found (unter exception)."
                            )
                else:                    
                    level, status = "errors", 0
                    msg = (
                        f"Invalid order found for '{name}'"
                    )
                    if verbose:
                        logging.error(
                            f"Variable: {name:<12} {' '*59} --> "
                            f"NOK, Invalid order found"
                        )
            else:      
                level, status = "errors", 0
                msg = (
                    f"Invalid values found for '{name}'"
                )
                if verbose:
                    logging.error(
                        f"Variable: {name:<12} {' '*59}--> "
                        f"NOK, Invalid values found"
                    )
        outcome.setdefault(level, []).append(msg)
        outcome["status"] = status
    
    #print(outcome)
    return outcome

# Test 20. Check the units of the variables.
@register(CONVENTION, "c3s_variable_units")
def c3s_19_units_check(
    ds: Dataset, 
    spec: dict, 
    excep: dict, 
    verbose, operational) -> dict:
    if verbose:
        logging.info("Check the units of the variables.")
    outcome = {"status": 1}
    if operational:
        if verbose:
            logging.info(
                f"Operational check is the same with the non operational check!"
                ) 
    
    for var_name, nc_var in ds.variables.items():            
        status_flag = True
        attrs = nc_var.ncattrs()
        
        standard_name = ""
        try:
            standard_name = nc_var.getncattr("standard_name")
        except AttributeError:
            pass

        if "units" in attrs:
            units_attr = nc_var.getncattr("units")
            deprecated_units = ("level", "layer", "sigma_level")
            cf_units_modifiers = {
                "detection_minimum": None, 
                "number_of_observations": "1", 
                "standard_error": None, 
                "status_flag": None
                }
            if not isinstance(units_attr, str):
                status_flag = False
                outcome["status"] = 0
                err_msg = (
                    f"Attribute 'units' of variable '{var_name}' must be a string "
                    f"(currently '{type(units_attr)}'"
                )
                outcome.setdefault("errors", []).append(err_msg)
                if verbose:
                    logging.error(
                        f"Value of attribute 'units' of variable '{var_name}' --> "
                        f"NOK, must be a string --> Actual ({type(units_attr)})")
            
            elif units_attr in deprecated_units:
                status_flag = True
                wrn_msg = (
                    f"Value of attribute 'units' of variable '{var_name}' is "
                    f"deprecated: '{units_attr}'. No further checks done."
                )
                outcome.setdefault("warnings", []).append(wrn_msg)
                if verbose:
                    logging.warning(
                        f"Value of attribute 'units' of variable '{var_name}' --> "
                        f"OK, deprecated: '{units_attr}'. No further checks done.")
            else:
                units = Units(units_attr)
                if not units.isvalid:
                    outcome["status"] = 0
                    outcome.setdefault("errors", []).append(
                        f"Value of attribute 'units' of variable '{var_name}' "
                        f"is invalid: '{units}'")
                    if verbose:
                        logging.error(
                            f"Value of attribute 'units' of variable '{var_name}' --> "
                            f"NOK, is invalid: '{units}'")
                    status_flag = False
                
            if standard_name:                        
                __std_names_tree = ElementTree.parse(
                    resource_filename("c3schecker", "resources/cf-standard-name-table.xml")
                    )
                for elt in __std_names_tree.iter("entry"):
                    if elt.attrib["id"] == standard_name:
                        cfcheck = {"units": elt.findtext("canonical_units"),                    
                                    "grib": elt.findtext("grib"),
                                    "amip": elt.findtext("amip"),
                                    "description": elt.findtext("description"),}
                u = Units(cfcheck["units"])
                if u.islatitude:
                    pass
                elif u.islongitude:
                    pass
                elif var_name == "leadtime":
                    if str(units_attr) == str(units):
                        status_flag = True
                elif var_name == "reftime":
                    if str(units_attr) == str(units):
                        status_flag = True
                elif var_name == "time":
                    if str(units_attr) == str(units):
                        status_flag = True
                elif ds.level_type == "ocean2d":
                    if str(units_attr) == str(units):
                        status_flag = True
                elif str(units_attr) not in str(cfcheck["units"]):
                    institute_id = ds.institute_id
                    system = ds.source.split()[0][:-1]
                    exceptions = excep.get(
                        "exceptions", {}).get(institute_id, {}).get(
                            system, {}).get("units", {}).get(var_name, {}
                            )
                    if units_attr not in exceptions:
                        status_flag = False
                        outcome["status"] = 0
                        outcome.setdefault("errors", []).append(
                            f"Variable '{var_name}' (units: {units_attr}): NOK. "
                            f"Expected CF units {cfcheck['units']}"
                            )
                        if verbose:
                            logging.error(
                                f"Variable:  {var_name:<15}  units seems "
                                f"not correct. Please further check with CF Checks"
                                )
                            logging.error(
                                f"Variable:  {var_name:<15}  units: " 
                                f"{units_attr:<40} --> NOK. Expected units "
                                f"{cfcheck['units']}"
                                )   
                    else:
                        status_flag = False
                        outcome.setdefault("warnings", []).append(
                            f"Variable '{var_name}' (units: {units_attr}): NOK. "
                            f"Expected CF units {cfcheck['units']}. "
                            f"Under expection for {institute_id} : {system}"
                            )
                        if verbose:
                            logging.warning(
                                f"Variable:  {var_name:<15}  "
                                f"units: {units_attr:<40} --> OK, expected CF "
                                f"units {cfcheck['units']} (under expection "
                                f"for {institute_id} : {system})"
                                )                          
            if status_flag:
                if verbose:
                    logging.info(
                        f"Variable:  {var_name:<15}  "
                        f"units: {units_attr:<40} --> OK"
                        )
                outcome.setdefault("info", []).append(f"'{var_name}' units OK")
        else:
            if verbose:
                logging.info(f"Variable:  {var_name:<15}  without units {' '*33} --> OK")
            outcome.setdefault("info", []).append(f"'{var_name}' without units")

    # print(status_flag)
    # if status_flag:
    #     status = 1
    # else:
    #     status = 0
    # outcome["status"] = status
    #print(outcome)
    return outcome

# Test 21. Checks the consistency of leadtime_bnds with the correspondent
# coordinate; leadtime should be in the center of the boundaries interval
# for example, if leadtime_bnds[n,:] = [48,72], then leadtime=50
@register(CONVENTION, "c3s_time_bnds_consistency")
def c3s_leadtime_bnds_coordinates_check(
    ds: Dataset, 
    spec: dict, 
    excep: dict, 
    verbose, operational
    ) -> dict: 
    if verbose:
        logging.info(
            "Checks the consistency of time intervals with the correspondent "
            "coordinate."
        )
    if operational:
        if verbose:
            logging.info(
                f"Operational check is the same with the non operational check!"
                ) 
    status = 1
    outcome = {"status": status}

    constraints = spec.get("time_coordinates_values_per_var_name")
    actual_data_vars = _get_data_vars(ds)
    scientific_var_name = actual_data_vars[0].name

    if ds.frequency == 'fix':
        if verbose:
            logging.info("Fixed frequency. No time-related coordinates.")
        outcome.setdefault("info", []).append(
            f"[Fixed frequency. No time-related coordinates]"
            )
        return outcome
    
    try:
        cell_methods = constraints.get(scientific_var_name)["cell_methods"]
    except:
        status = 0
        outcome.setdefault("errors", []).append(
            f"Variable ({scientific_var_name}) is not a C3S "
            f"parameter"
        )
        if verbose:
            logging.error(
                f"Variable: ({scientific_var_name}) is not a C3S "
                f"parameter. Do not continue the check "
                f"{' '*70} --> NOK"
            )
            
        outcome["status"] = status
        return outcome


    if cell_methods == "point":
        outcome.setdefault("info", []).append(
            f"Instantaneous variable. No boundaries."
            )
        if verbose:
            logging.info("Instantaneous variable. No boundaries.")
        return outcome

    leadt  = ds.variables['leadtime'][:]
    leadt_units = ds.variables['leadtime'].units
    leadt_bnds  = ds.variables['leadtime_bnds'][:]

    # expected_step could not be easily defined for the ocean variables 
    # frequency = mon and the step depends on the month. 
    # expected_step = constraints.get(scientific_var_name)["step"]
    
    step = 0
    for n in range(len(leadt)): 
        center = (leadt_bnds[n][1] - leadt_bnds[n][0])/2 + step
        step = (leadt_bnds[n][1] - leadt_bnds[n][0]) + step
        if center == leadt[n]:
            result = True
        else:
            result = False
            status = 0 
            if verbose:
                logging.error(
                    f"Not correct leadtime boundary: {str(leadt_bnds[n]):<15}, "
                    f"actual value of the leadtime variable: "
                    f"{str(leadt[n]):<10} not in the middle {' '*8} --> NOK"
                )

    if result:
        outcome.setdefault("info", []).append(
            f"The values of leadtime variable is in the center of the "
            f"leadtime boundary --> OK"
        )
        if verbose:
            logging.info(
                f"The values of leadtime variable is in the center of the "
                f"leadtime boundary {' '*50} --> OK"
            )
            logging.info(
                f"First boundary leadtime boundary: {str(leadt_bnds[0]):<15}; "
                f"Value of the leadtime variable: "
                f"{str(leadt[0]):<20} {' '*20} --> OK"
            )
    else:
        outcome.setdefault("errors", []).append(
            f"The values of leadtime variable is not in the center of the "
            f"leadtime boundary --> NOK"
        )
        if verbose:
            logging.error(
                f"The values of leadtime variable is not in the center of the "
                f"leadtime boundary {' '*46} --> NOK"
            )
        #     for i in range(len(leadt_bnds)):
        #         logging.error(
        #             f"First boundary leadtime boundary: {str(leadt_bnds[i]):<15}; "
        #             f"Value of the leadtime variable: "
        #             f"{str(leadt[i]):<20} {' '*20} --> NOK"
        #         )
        
    outcome["status"] = status   
    #print(outcome)
    return outcome

#############################
# Test 22. Check the consistency of the leadtime and leadtime_bnds.
@register(CONVENTION, "c3s_time_values")
def c3s_time_values_check(  
    ds: Dataset, 
    spec: dict, 
    excep: dict, 
    verbose, operational
    ) -> dict: 
    if verbose:
        logging.info(
            "Checks the values of the time coordinates."
            )
    if operational:
        if verbose:
            logging.info(
                f"Operational check is the same with the non operational check!"
                ) 
    outcome = {"status": 1}
    constraints = spec.get("time_coordinates_values_per_var_name")
    actual_data_vars = _get_data_vars(ds)
    scientific_var_name = actual_data_vars[0].name
    
    if ds.frequency == 'fix':
        if verbose:
            logging.info("Fixed frequency. No time-related coordinates.")
        outcome.setdefault("info", []).append(
            f"[Fixed frequency. No time-related coordinates]"
            )
        return outcome

    leadt  = ds.variables['leadtime'][:]
    leadt_units = ds.variables['leadtime'].units

    try:
        cell_method = constraints.get(scientific_var_name)["cell_methods"]
        step = constraints.get(scientific_var_name)["step"]
    except:
        status = 0
        outcome.setdefault("errors", []).append(
            f"Variable ({scientific_var_name}) is not a C3S "
            f"parameter"
        )
        if verbose:
            logging.error(
                f"Variable: ({scientific_var_name}) is not a C3S "
                f"parameter. Do not continue with the check "
                f"{' '*70} --> NOK"
            )
        outcome["status"] = status
        return outcome

    if cell_method == "point":
        start_point = step
    else:
        start_point = step / 2

    leadt_computed = np.array(
        [ start_point + (step*n) for n in range(len(leadt))]
    )

    if np.all(np.isin(leadt, leadt_computed)):
    
        status = 1
        outcome.setdefault("info", []).append(
            f"Variable leadtime: values as expected OK"
        )
        if verbose: 
            logging.info(
                f"Variable {str('leadtime'):15}: values as expected, "
                f"range [{str(leadt[0]):<4}, {str(leadt[-1]):<7}], "
                f"frequency {str(step):<3} {str(leadt_units):10} "
                f"{' '*8} --> OK"
            ) 
            # logging.info(
            #     f"Variable {str('leadtime'):15}: Range [{leadt[0]}, "
            #     f"{leadt[-1]}] {' '*10} Frequency: "
            #     f"{step} {leadt_units:<19} Cell method: {cell_method} {' '*26} --> OK"
            #     )   
    else:
        if ds.level_type == "ocean2d":
            status = 1
            leadt = ds.variables['leadtime'][:] 
            outcome.setdefault("warnings", []).append(
                f"Variable leadtime: ocean variable, visual inspection [{leadt}]"
            )
            if verbose: 
                logging.warning(
                    f"Variable {str('leadtime'):<15}: visual inspection for ocean variables "
                    f"{leadt}"
                )
        else:
            status = 0
            outcome.setdefault("errors", []).append(
                f"Variable leadtime: Unexpected values were found"
            )
            if verbose: 
                logging.error(
                    f"Variable {str('leadtime'):15}: Unexpected values were found "
                    f"{' '*47} -->  NOK"
                    )   
        
    if cell_method not in "point" and ds.level_type not in "ocean2d":
        center = step / 2
        leadt_bnds  = ds.variables['leadtime_bnds'][:]    
        validt_computed = np.array(
            [ (n - center,  n + center) for n in leadt]
        )
        if np.all(validt_computed == leadt_bnds):
            status = 1
            outcome.setdefault("info", []).append(
                f"Variable leadtime_bnds: values as expected."
            )
            if verbose: 
                logging.info(
                    f"Variable {str('leadtime_bnds'):<15}: values as expected, boundaries "
                    f"start {str(validt_computed[0][0]):<3} end: "
                    f"{str(validt_computed[-1][-1]):<8} {' '*45} --> OK"
                )
        else:
            status = 0
            outcome.setdefault("errors", []).append(
                f"Variable leadtime_bnds: Unexpected values were found"
            )
            if verbose: 
                logging.error(
                    f"Variable leadtime_bnds  : Unexpected values were found "
                    f"expected boundaries start: "
                    f"{validt_computed[0][0]} end: {validt_computed[-1][-1]} "
                    f"actual boundaries start: "
                    f"{leadt_bnds[0][0]} end: {leadt_bnds[-1][-1]} "
                    f"--> NOK"
                )
    elif ds.level_type == "ocean2d":
        leadt_bnds  = ds.variables['leadtime_bnds'][:] 
        if verbose: 
            logging.warning(
                f"Variable {str('leadtime_bnds'):<15}: visual inspection: "
                f"{leadt_bnds}"
            )
    
    time  = ds.variables['time'][:]
    
    if np.all(leadt == time):
        outcome.setdefault("info", []).append(
            f"leadtime and time values are equal, values OK"
        )
        if verbose:
            logging.info(
                f"Variable {str('time'):<15}: leadtime and time values are equal "
                f"[leadtime == time] {' '*22} --> OK"
            )
    else:
        status = 0
        outcome.setdefault("errors", []).append(
            f"leadtime and time values are not equal, values NOK"
        )
        if verbose:
            logging.error(
                f"Variable {str('time'):<15}: leadtime and time values are not equal "
                f"[leadtime != time] {' '*22} --> OK"
            )

    if cell_method not in "point":
        #leadt_bnds  = ds.variables['leadtime_bnds'][:]
        try:
            time_bnds  = ds.variables['time_bnds'][:]
            if np.all(leadt_bnds == time_bnds):
                outcome.setdefault("info", []).append(
                    f"leadtime_bnds and time_bnds values are equal, values OK"
                )
                if verbose:
                    logging.info(
                        f"Variable {str('time_bnds'):<15}: leadtime_bnds and "
                        f"time_bnds values are equal "
                        f"[leadtime_bnds == time_bnds] {' '*2} --> OK"
                    )
            else:
                status = 0
                outcome.setdefault("errors", []).append(
                    f"leadtime_bnds and time_bnds values are not equal, values NOK"
                )
                if verbose:
                    logging.info(
                        f"Variable {str('time_bnds'):<15}: leadtime_bnds and "
                        f"time_bnds values are not equal "
                        f"[leadtime_bnds != time_bnds] {' '*20} --> NOK"
                    )
        except:
            status = 0
            outcome.setdefault("errors", []).append(
                f" time_bnds: No such variable NOK"
            )
            if verbose:
                logging.info(
                    f"Variable {str('time_bnds'):<15}: no such variable "
                    f" {' '*20} --> NOK"
                )


    outcome["status"] = status   
   
    #print(outcome)
    return outcome
#############################

# Test 22. Check the consistency of the leadtime and leadtime_bnds.
@register(CONVENTION, "c3s_time_consistency")
def c3s_20_time_coordinates_check(  
    ds: Dataset, 
    spec: dict, 
    excep: dict, 
    verbose, operational
    ) -> dict: 
    if verbose:
        logging.info(
            "Checks the consistency of time-related "
            "coordinates & auxiliary coordinates."
            )
    if operational:
        if verbose:
            logging.info(
                f"Operational check is the same with the non operational check!"
                ) 
    outcome = {"status": 1}
    institute_id = ds.institute_id
    system = ds.source.split()[0].split(":")[0]

    if ds.frequency == 'fix':
        if verbose:
            logging.info("Fixed frequency. No time-related coordinates.")
        outcome.setdefault("info", []).append(
            f"[Fixed frequency. No time-related coordinates]"
            )
        return outcome
    
    try:
        reft = datetime.datetime.strptime(ds.forecast_reference_time, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError as e:
        outcome.setdefault("warning", []).append(f"Unexpected time: {e}")
        outcome.setdefault("errors", []).append(f"Unexpected time: {e}")
        if verbose: 
            logging.warning(f"Unexpected time: {e}  -->  NOK")
    try:
        validt = nc.num2date(ds.variables['time'][:], ds.variables['time'].units)
    except:
        validt = []
        outcome.setdefault("warning", []).append(f"No data")
        outcome.setdefault("errors", []).append(f"No data")
        if verbose: 
            logging.warning(f"No data  -->  NOK")

    leadt  = ds.variables['leadtime'][:]
    leadt_units = ds.variables['leadtime'].units

    if leadt_units == 'days':
        unitfix = 86400.
        #msg_status = "info"
        outcome.setdefault("info", []).append(f"time coordinates units OK")
        #message = f"[time coordinates OK]"
        if verbose: 
            logging.info(f"{str('Time coordinates: leadtime units days'):<100} -->  OK")  
    elif leadt_units == 'hours':
        unitfix = 3600.
        #msg_status = "info"
        #message = f"[time coordinates OK]"
        outcome.setdefault("info", []).append(f"time coordinates units OK")
        if verbose: 
            logging.info(f"{str('Time coordinates: leadtime units hours'):<100}  -->  OK") 
    elif leadt_units == 'seconds':
        unitfix = 1.
        #msg_status = "info"
        #message = f"[time coordinates OK]"
        outcome.setdefault("info", []).append(f"time coordinates units OK")
        if verbose: 
            logging.info(f"{str('Time coordinates: leadtime units seconds'):<100}  -->  OK") 
    else:
        if verbose: 
            logging.error(
                f"Unexpected units for 'leadtime' coordinate: {leadt_units}  --> NOK"
                )
        status = 0
        outcome.setdefault("errors", []).append(
            f"Unexpected units for 'leadtime' coordinate: {leadt_units}"
            )
    validt_computed = np.array([reft + datetime.timedelta(seconds=unitfix*ll) for ll in leadt])
    try:
        dift = abs(validt - validt_computed).sum().total_seconds()
    except:
        dift = 1

    if dift != 0:
        if verbose: 
            logging.error(
                f"Wrong values in time coordinates: "
                f"[time != forecast_reference_time + leadtime]  -->  NOK")       
        status = 0
        outcome.setdefault("errors", []).append(
            f"Wrong values in time coordinates: "
            f"[time != forecast_reference_time + leadtime]")
    else:
        status = 1
        outcome.setdefault("info", []).append(
            f"Time coordinates: [time = forecast_reference_time "
            f"+ leadtime] -->  OK"
            )
        if verbose: 
            logging.info(
                f"Time coordinates: [time != forecast_reference_time "
                f"+ leadtime] {' '*38} -->  OK"
                )   

    outcome["status"] = status   
    #print(outcome)
    return outcome

#############################

# Test 22. # Checks the consistency of missing value indicators for.
@register(CONVENTION, "c3s_missing_values_consistency")
def c3s_21_missing_values_check(
    ds: Dataset, 
    spec: dict, 
    excep: dict, 
    verbose, operational
    ) -> dict: 

    outcome = {"status": 1}
    institute_id = ds.institute_id
    system = ds.source.split()[0].split(":")[0]
    exceptions = excep.get("exceptions", {}).get(
        institute_id, {}).get(system, {}).get("missing_values", {}
                                              )
    status = 1

    if verbose:
        logging.info(
            "Checks the consistency of missing value indicators."
            )

    vars = {}            
    for k, v in list(ds.variables.items()):
        coord_bounds_scala_var = [
            "hcrs", "lat", "lat_bnds", 
            "lon", "lon_bnds", "plev", "leadtime",
            "reftime", "time", "realization", "depth" 
            ]
        if k not in coord_bounds_scala_var:
            vars[k] = v

    thisvar=ds[list(vars.keys())[0]]
    thisFV = thisvar.getncattr(
        '_FillValue') if '_FillValue' in thisvar.ncattrs() else None
    thismv = thisvar.getncattr(
        'missing_value') if 'missing_value' in thisvar.ncattrs() else None

    
    if not thisFV or not thismv:
        outcome.setdefault("info", []).append(
                f"The attributes  '_FillValue', 'missing_value' "
                f"were not found"
            )
        if verbose:
            logging.info(
                f"The attributes  '_FillValue', 'missing_value' "
                f"were not found"
            )

    if thisFV!=thismv:
        
        if thisvar.name in exceptions:
            outcome.setdefault("warnings", []).append(
                    f"The data array does have missing values, "
                    f"but inconsistent attributes: "
                    f"missing_value={str(thismv)} "
                    f"_FillValue={str(thisFV)}. Under exception."
                    )
            if verbose:
                logging.warning(
                    f"Variable: {list(vars.keys())[0]} "
                    f"The data array does have missing values, "
                    f"but inconsistent attributes:  "
                    f"missing_value={str(thismv)} "
                    f"_FillValue={str(thisFV)}. Under "
                    f"exception  -->  OK --> Under exception"
                    )
        
        else:
            outcome.setdefault("errors", []).append(
                f"Inconsistent attributes: "
                f"missing_value={str(thismv)} "
                f"_FillValue={str(thisFV)}"
                )
            if verbose:
                logging.error(
                    f"Variable: {list(vars.keys())[0]} --> "
                    f"NOK --> Inconsistent attributes:  "
                    f"missing_value={thismv}   _FillValue={thisFV}"
                    )
            status = 0
        msg_status = "errors"
    
    elif thisFV is not None:
        
        a_thisvar = thisvar[:].filled() if np.ma.is_masked(thisvar[:]) else thisvar[:]    
        # bad/missing values may not be properly masked
        # https://www.unidata.ucar.edu/support/help/MailArchives/python/msg00042.html 
        if thisFV not in a_thisvar:
            if thisvar.name in exceptions:
                outcome.setdefault("warning", []).append(
                    f"The data array does not have missing values "
                    f"(missing_value=_FillValue={thisFV} not needed).'")
                if verbose:
                    logging.warning(
                    f"Variable: {list(vars.keys())[0]} --> OK --> "
                    f"The data array does not have missing values "
                    f"(missing_value=_FillValue={thisFV} "
                    f"not needed).  --> Under exception"
                    )
            else: 
                outcome.setdefault("errors", []).append(
                    f"The data array does not have missing "
                    f"values (missing_value=_FillValue={thisFV} not needed).'"
                    )
                if verbose:
                    logging.error(
                        f"Variable: {list(vars.keys())[0]} --> NOK "
                        f"--> The data array does not have missing "
                        f"values (missing_value=_FillValue={thisFV} not needed).")
                status = 0
        
    else:
        if verbose:
            logging.info(f"Missing values and _FillValue  {' '*70} -->  OK")  
        outcome.setdefault("info", []).append(f"Missing values and _FillValue OK") 
    
    outcome["status"] = status
    #print(outcome)
    return outcome


# test 23. Realization content
@register(CONVENTION, "c3s_realization_format")
def c3s_realization_content_check(
    ds: Dataset, 
    spec: dict, 
    excep: dict, 
    verbose, operational
    ) -> dict: 
    if verbose:
        logging.info(
            "Check the if the realization variable follows SPECS approach"
            )
    if operational:
        if verbose:
            logging.info(
                "Operational check is the same with the non operational check!"
                )
    outcome = {"status": 1}
    institute_id = ds.institute_id
    system = ds.source.split()[0].split(":")[0] 

    try:
        if ds.frequency=='fix' and ds.institute_id=='egrr':
            ripstr = 'r000i000p000'
        else:
            ripvar = ds.variables['realization'][:]
            # in python3 ripvar is an array of 'byte' characters
            # using b"" and .decode() is backwards compatible with python2
            ripstr = b"".join(ripvar.filled()).decode() if np.ma.is_masked(
                ripvar) else b"".join(ripvar).strip().decode()
        
        actual_value = ripstr
        expected_value = re.compile(r"^r([0-9]+)i([0-9]+)p([0-9]+)$")
        check_result = re.match(expected_value, actual_value)
        
        if not check_result:
            if verbose:
                logging.error(
                    f"Realization doesn't follow the "
                    f"SPECS approach (rXXiYYpZZ)          --> NOK"
                    )
                logging.error(
                    f"Actual values {actual_value}. Expected "
                    f"values {expected_value}     --> NOK"
                    )
            status = 0
            msg_status = "errors"
            message = [
                f"Realization doesn't follow the SPECS approach (rXXiYYpZZ)"
                ] 
        else: 
            if verbose:
                space = " "
                logging.info(
                    f"Realization follows the SPECS approach {space*63} --> OK"
                    )
                logging.info(
                    f"Realization: {actual_value:<15} {space*73} --> OK"
                    )
            status = 1
            msg_status = "info"
            message = ['Realization OK']

    except:
        status = 0
        msg_status = "errors"
        message = "Realization test failed. Probably the ensemble coordinate is missing."
        if verbose:
            logging.error(
                f"Realization test failed. Probably "
                f"the ensemble coordinate is missing."
                )

    outcome["status"] = status
    outcome[msg_status] = message
    
    #print(outcome)
    return outcome



# def _data_check(_type, ds, spec, check_logic, fail_msg, success_msg):
#     constraints = spec.get(_type, {})
#     if not constraints:
#         return {"status": 1, "info": ["No constraints -> Skipped"]}

#     def _do_check(variable_name, expected, mandatory_constraint, out, **kwargs):
#         try:
#             results = check_logic(ds, variable_name, expected, **kwargs)
#         except KeyError:
#             return
#         if results["failure"]:
#             if mandatory_constraint:
#                 level, status = "errors", 0
#             else:
#                 level, status = "warnings", 0
#             msg = fail_msg.format(**results)
#         elif results.get("warnings", False):
#             level, status = "warning", 1
#             msg = fail_msg.format(**results)
#         else:
#             level, status = "info", 1
#             msg = success_msg.format(**results)
#         out.setdefault(level, []).append(msg)
#         out["status"] = status

#     outcome = {"status": 1}
#     for name, var_spec in constraints.get("expected", {}).items():
#         try:
#             mandatory = var_spec.pop("mandatory")
#         except KeyError:
#             mandatory = True
#         if name == "default":
#             for var_name, expected_value in var_spec.items():
#                 _do_check(var_name, expected_value, mandatory, outcome)
#         else:
#             try:
#                 nc_var = ds.variables[name]
#             except KeyError:
#                 continue
#             cell_method_condition = var_spec.get("with_cell_methods")
#             if cell_method_condition is not None:
#                 if nc_var.cell_methods == cell_method_condition:
#                     continue
#             for dimension, expected_value in var_spec["dimensions"].items():
#                 # TODO: Do I have to check the config file at the same time? e.g:
#                 #  here the dim_name given in the config must be a valid dim of the
#                 #  specified variable
#                 for var_dimension in nc_var.dimensions:
#                     if var_dimension == dimension:
#                         _do_check(
#                             name, expected_value, mandatory, outcome, dim_name=dimension
#                         )
#     return outcome


def _ncattr_present(value):
    return value is not None


def _simple_equality_check(actual, constraints, warning_msgs, error_msgs):
    if not constraints:
        return {"status": 1, "info": ["No constraints -> Skipped"]}
    expected = constraints["expected"]
    if actual == expected:
        outcome = {"status": 1, "info": ["Test successful OK"]}
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

def _get_data_vars(dataset):
        return dataset.get_variables_by_attributes(coordinates=_ncattr_present)
