"""Unit tests for C3S Seasonal Forecast Checking"""
import numpy as np
import pytest
from netCDF4 import Dataset

from c3schecker.cop.Cpchecker import Cpchecker

CHECK_TYPE = "seasonal"


@pytest.fixture
def dataset_with_valid_file_format():
    ds = Dataset(
        "not_saved.nc",
        mode="w",
        clobber=False,
        diskless=True,
        persist=False,
        format="NETCDF4_CLASSIC",
    )
    yield ds
    ds.close()


@pytest.fixture
def dataset_with_invalid_file_format():
    # Default format is NETCDF4, which is invalid in the context of C3S-0.1
    ds = Dataset("not_saved.nc", mode="w", clobber=False, diskless=True, persist=False)
    yield ds
    ds.close()


@pytest.fixture
def ds_lat_lon_dims(dataset_with_valid_file_format):
    dataset_with_valid_file_format.createDimension("lon", 360)
    dataset_with_valid_file_format.createDimension("lat", 180)
    yield dataset_with_valid_file_format


@pytest.fixture
def ds_one_var_2_dimensions(ds_lat_lon_dims):
    ds_lat_lon_dims.createVariable("foo", np.float, ("lon", "lat"))
    yield ds_lat_lon_dims


@pytest.fixture
def ds_2_vars_2_dimensions(ds_one_var_2_dimensions):
    ds_one_var_2_dimensions.createVariable("bar", np.float, ("lon", "lat"))
    yield ds_one_var_2_dimensions


@pytest.fixture(
    params=[
        "plev",
        "depth",
        "height",
        "realization",
        "time",
        "time_bnds",
        "leadtime_bnds",
        "lat_bnds",
        "lon_bnds",
        "depth_bnds",
        "str31",
        "leadtime",
    ]
)
def ds_with_auth_dims(request, ds_lat_lon_dims):
    ds_lat_lon_dims.createDimension(request.param, 1)
    yield ds_lat_lon_dims


@pytest.fixture
def ds_with_unauth_dims(ds_lat_lon_dims):
    ds_lat_lon_dims.createDimension("foo", 1)
    yield ds_lat_lon_dims


@pytest.fixture
def ds_all_dimensions(ds_lat_lon_dims):
    ds_lat_lon_dims.createDimension("leadtime")
    ds_lat_lon_dims.createDimension("str31", 31)
    ds_lat_lon_dims.createDimension("bnds", 2)
    ds_lat_lon_dims.createDimension("plev", 11)
    ds_lat_lon_dims.createDimension("depth", 1)
    yield ds_lat_lon_dims


@pytest.fixture
def ds_with_mandatory_attrs_per_std_name(ds_all_dimensions):
    variables = {
        "time": {
            "_dim": ("leadtime",),
            "_type": np.float,
            "units": "hours since 2020-01-01 00:00:00",
            "calendar": "gregorian",
            "long_name": "Verification time of the forecast",
            "standard_name": "time",
            "bounds": "time_bnds",
        },
        "reftime": {
            "_dim": (),
            "_type": np.float,
            "units": "hours since 2020-01-01T00:00:00Z",
            "calendar": "gregorian",
            "long_name": "Start date of the forecast",
            "standard_name": "forecast_reference_time",
        },
        "leadtime": {
            "_dim": ("leadtime",),
            "_type": np.float,
            "units": "hours",
            "long_name": "Time elapsed since the start of the forecast",
            "standard_name": "forecast_period",
            "bounds": "leadtime_bnds",
        },
        "latitude": {
            "_dim": ("lat",),
            "_type": np.float,
            "axis": "Y",
            "units": "degrees_north",
            "long_name": "latitude",
            "valid_min": -90.0,
            "valid_max": 90.0,
            "bounds": "lat_bnds",
            "standard_name": "latitude",
        },
        "longitude": {
            "_dim": ("lon",),
            "_type": np.float,
            "axis": "X",
            "units": "degrees_east",
            "long_name": "longitude",
            "valid_min": 0.0,
            "valid_max": 360.0,
            "bounds": "lon_bnds",
            "standard_name": "longitude",
        },
        "air_pressure": {
            "_dim": ("plev",),
            "_type": np.float,
            "axis": "Z",
            "units": "Pa",
            "long_name": "pressure",
            "positive": "down",
            "standard_name": "air_pressure",
        },
        "depth": {
            "_dim": ("depth",),
            "_type": np.float,
            "units": "m",
            "long_name": "depth",
            "axis": "Z",
            "positive": "down",
            "standard_name": "depth",
            "bounds": "depth_bounds",
        },
        "height": {
            "_dim": (),
            "_type": np.float,
            "units": "m",
            "long_name": "height",
            "axis": "Z",
            "positive": "up",
            "standard_name": "height",
            "valid_min": 0,
            "valid_max": 0,
        },
        "realization": {
            "_dim": ("str31",),
            "_type": np.dtype("|S1"),
            "units": "1",
            "axis": "E",
            "standard_name": "realization",
            "long_name": "realization",
        },
    }
    for var, props in variables.items():
        nc_var = ds_all_dimensions.createVariable(
            var, props.pop("_type"), props.pop("_dim")
        )
        nc_var.setncatts(props)
    yield ds_all_dimensions


@pytest.fixture
def ds_lat_var_without_bounds_attr(ds_all_dimensions):
    lat_var_attrs_without_bounds = {
        "axis": "Y",
        "units": "degrees_north",
        "long_name": "latitude",
        "valid_min": -90.0,
        "valid_max": 90.0,
        "standard_name": "latitude",
    }
    lat_var = ds_all_dimensions.createVariable("lat", np.float, ("lat",))
    lat_var.setncatts(lat_var_attrs_without_bounds)
    yield ds_all_dimensions


@pytest.fixture(params=[("calendar", "gregorian")])
def ds_with_mandatory_attr_values(request, ds_with_mandatory_attrs_per_std_name):
    attr_name, attr_value = request.param
    for variable in ds_with_mandatory_attrs_per_std_name.variables.values():
        var_attrs = variable.ncattrs()
        if attr_name in var_attrs:
            variable.setncattr(attr_name, attr_value)
    yield ds_with_mandatory_attrs_per_std_name


@pytest.fixture(params=[("calendar", "julian")])
def ds_with_bad_mandatory_attr_values(request, ds_with_mandatory_attrs_per_std_name):
    attr_name, attr_value = request.param
    for variable in ds_with_mandatory_attrs_per_std_name.variables.values():
        var_attrs = variable.ncattrs()
        if attr_name in var_attrs:
            variable.setncattr(attr_name, attr_value)
    yield ds_with_mandatory_attrs_per_std_name


@pytest.fixture()
def ds_with_mandatory_attributes_per_variable_name(
    ds_with_mandatory_attrs_per_std_name
):
    # We explicitly choose a variable that has the cell_methods attributes so that we
    # can test for the case when a variable has an attribute that must match a regex
    va = {
        "long_name": "Northward Wind",
        "units": "m s-1",
        "coordinates": "reftime realization time leadtime plev lat lon",
        "standard_name": "y_wind",
        "cell_methods": "leadtime: point",
        "grid_mapping": "hcrs",
        "dimensions": ["leadtime", "plev", "lat", "lon"],
        "frequency": "12hr",
        "level_type": "pressure",
        "modeling_realm": "atmos",
    }
    nc_var = ds_with_mandatory_attrs_per_std_name.createVariable(
        "va", np.float, va.pop("dimensions")
    )
    nc_var.setncatts(va)
    yield ds_with_mandatory_attrs_per_std_name


@pytest.fixture(
    params=[
        # First case: missing mandatory attribute cell_methods
        {
            "long_name": "Northward Wind",
            "units": "m s-1",
            "coordinates": "reftime realization time leadtime plev lat lon",
            "standard_name": "y_wind",
            "grid_mapping": "hcrs",
            "dimensions": ["leadtime", "plev", "lat", "lon"],
            "frequency": "12hr",
            "level_type": "pressure",
            "modeling_realm": "atmos",
        },
        # Second case: missing mandatory attribute units,
        # cell_methods with wrong expected regex
        {
            "long_name": "Northward Wind",
            "coordinates": "reftime realization time leadtime plev lat lon",
            "standard_name": "y_wind",
            "cell_methods": "garbage",
            "grid_mapping": "hcrs",
            "dimensions": ["leadtime", "plev", "lat", "lon"],
            "frequency": "12hr",
            "level_type": "pressure",
            "modeling_realm": "atmos",
        },
    ]
)
def ds_without_mandatory_attributes_per_variable_name(
    request, ds_with_mandatory_attrs_per_std_name
):
    va = request.param
    nc_var = ds_with_mandatory_attrs_per_std_name.createVariable(
        "va", np.float, va["dimensions"]
    )
    nc_var.setncatts({k: v for k, v in va.items() if k != "dimensions"})
    yield ds_with_mandatory_attrs_per_std_name


@pytest.fixture
def ds_without_mandatory_dim_for_variable(ds_with_mandatory_attrs_per_std_name):
    # Create a variable without dimensions
    va = {
        "long_name": "Northward Wind",
        "units": "m s-1",
        "coordinates": "reftime realization time leadtime plev lat lon",
        "standard_name": "y_wind",
        "cell_methods": "leadtime: point",
        "grid_mapping": "hcrs",
        "frequency": "12hr",
        "level_type": "pressure",
        "modeling_realm": "atmos",
    }
    nc_var = ds_with_mandatory_attrs_per_std_name.createVariable("va", np.float)
    nc_var.setncatts(va)
    yield ds_with_mandatory_attrs_per_std_name


@pytest.fixture
def ds_with_all_mandatory_global_attr_content(dataset_with_valid_file_format):
    mandatory_global_attrs_values = {
        "Conventions": "CF-1.6 C3S-0.1",
        "summary": (
            "Seasonal Forecast data produced by ECMWF as its contribution "
            "to the seasonal forecast activity of the Copernicus Climate Change "
            "Service (C3S). The data has global coverage with a 1-degree "
            "horizontal resolution and spans for around 6 months since the "
            "start date"
        ),
        "title": "ECMWF seasonal forecast model output prepared for C3S",
        "forecast_type": "hindcast",
        "institute_id": "ecmf",
        "project": "C3S Seasonal Forecast",
        "contact": "http://copernicus-support.ecmwf.int",
        "keywords": (
            "Seasonal Forecasts, C3S, ECMWF, Copernicus, Climate Change, "
            "Climate Services, Earth Science Services, Environmental Advisories, "
            "Climate Advisories"
        ),
        "institution": (
            "ECMWF, European Centre for Medium-Range Weather Forecasts, "
            "Reading, United Kingdom"
        ),
        "history": "",
        "modeling_realm": "atmos",
        "frequency": "mon",
        "level_type": "surface",
    }
    dataset_with_valid_file_format.setncatts(mandatory_global_attrs_values)
    yield dataset_with_valid_file_format


@pytest.fixture
def ds_with_mandatory_global_attr_content_bad_value(dataset_with_valid_file_format):
    mandatory_global_attrs_values = {
        "Conventions": "CF-1.6 C3S-0.1",
        "summary": (
            "This is an unsupported summary. As Such, "
            "dataset_with_valid_file_format will not pass the check"
        ),
        "title": "ECMWF seasonal forecast model output prepared for C3S",
        "forecast_type": "hindcast",
        "institute_id": "ecmf",
        "project": "C3S Seasonal Forecast",
        "contact": "http://copernicus-support.ecmwf.int",
        "keywords": (
            "Seasonal Forecasts, C3S, ECMWF, Copernicus, Climate Change, "
            "Climate Services, Earth Science Services, Environmental Advisories, "
            "Climate Advisories"
        ),
        "institution": (
            "ECMWF, European Centre for Medium-Range Weather Forecasts, "
            "Reading, United Kingdom"
        ),
        "history": "",
        "modeling_realm": "atmos",
        "frequency": "mon",
        "level_type": "surface",
    }
    dataset_with_valid_file_format.setncatts(mandatory_global_attrs_values)
    yield dataset_with_valid_file_format


@pytest.fixture
def ds_with_all_global_mandatory_attrs(ds_with_all_mandatory_global_attr_content):
    other_global_attrs = {
        "comment": "This is a comment",
        "source": "Evian",
        "references": "A reference",
        "forecast_reference_time": "2020-08-17T12:32:00Z",
        "creation_date": "2020-08-17T12:32:00Z",
        "commit": "hash",
    }
    ds_with_all_mandatory_global_attr_content.setncatts(other_global_attrs)
    yield ds_with_all_mandatory_global_attr_content


@pytest.fixture
def ds_with_missing_val_in_kw_global_attr(dataset_with_valid_file_format):
    all_but_ecmwf = (
        "Seasonal Forecasts, C3S, Copernicus, Climate Change, "
        "Climate Services, Earth Science Services, Environmental Advisories, "
        "Climate Advisories"
    )
    dataset_with_valid_file_format.setncattr("keywords", all_but_ecmwf)
    yield dataset_with_valid_file_format


@pytest.fixture
def ds_with_bad_date_content_in_global_attrs(dataset_with_valid_file_format):
    fc_ref_time = "20200817123200Z"
    dataset_with_valid_file_format.setncattr("forecast_reference_time", fc_ref_time)
    yield dataset_with_valid_file_format


@pytest.fixture
def ds_with_specific_humidity(dataset_with_valid_file_format):
    q = {
        "long_name": "Specific humidity",
        "units": "1",
        "standard_name": "specific_humidity",
        "mars_paramid": "133",
    }
    nc_var = dataset_with_valid_file_format.createVariable("q", np.float)
    nc_var.setncatts(q)
    yield dataset_with_valid_file_format


@pytest.fixture
def ds_with_specific_humidity_malformed(dataset_with_valid_file_format):
    # Make a mistake in the specific humidity var (bad unit)
    q = {
        "long_name": "Specific humidity",
        "units": "m",
        "standard_name": "specific_humidity",
        "mars_paramid": "133",
    }
    nc_var = dataset_with_valid_file_format.createVariable("q", np.float)
    nc_var.setncatts(q)
    yield dataset_with_valid_file_format


class TestC3S01:
    CONVENTION = "CF-1.6 C3S-0.1"

    def test_meta_mandatory_cf_convention_ok(self, dataset_with_valid_file_format):
        dataset_with_valid_file_format.setncattr("convention", self.CONVENTION)
        self._check_success(
            dataset_with_valid_file_format, "1_meta.1_submeta.Mandatory_cf_convention"
        )

    def test_meta_mandatory_cf_convention_ko(self, dataset_with_valid_file_format):
        # First case: Invalid string for one of the bits
        dataset_with_valid_file_format.setncattr("convention", "CF-1.6 C3S-1")
        self._check_failure(
            dataset_with_valid_file_format, "1_meta.1_submeta.Mandatory_cf_convention"
        )

        # Second case: Inverted order of the valid bits
        reversed_convention = " ".join(reversed(self.CONVENTION.split()))
        dataset_with_valid_file_format.setncattr("convention", reversed_convention)
        self._check_failure(
            dataset_with_valid_file_format, "1_meta.1_submeta.Mandatory_cf_convention"
        )

    def test_mandatory_netcdf_format_ok(self, dataset_with_valid_file_format):
        self._check_success(
            dataset_with_valid_file_format, "1_meta.Mandatory_netcdf_format"
        )

    def test_mandatory_netcdf_format_ko(self, dataset_with_invalid_file_format):
        self._check_failure(
            dataset_with_invalid_file_format, "1_meta.Mandatory_netcdf_format"
        )

    def test_mandatory_number_datavariable_per_netcdf_ok(self, ds_one_var_2_dimensions):
        self._check_success(
            ds_one_var_2_dimensions, "1_meta.Mandatory_number_datavariable_per_netcdf"
        )

    def test_mandatory_number_datavariable_per_netcdf_ko(self, ds_2_vars_2_dimensions):
        self._check_failure(
            ds_2_vars_2_dimensions, "1_meta.Mandatory_number_datavariable_per_netcdf"
        )

    def test_mandatory_dimensions_ok(self, ds_lat_lon_dims):
        self._check_success(ds_lat_lon_dims, "1_meta.Mandatory_dimensions")

    def test_mandatory_dimensions_auth_ok(self, ds_with_auth_dims):
        self._check_success(ds_with_auth_dims, "1_meta.Mandatory_dimensions")

    def test_mandatory_dimensions_auth_ko(self, ds_with_unauth_dims):
        self._check_failure(ds_with_unauth_dims, "1_meta.Mandatory_dimensions")

    def test_mandatory_attributes_per_standardname_ok(
        self, ds_with_mandatory_attrs_per_std_name
    ):
        self._check_success(
            ds_with_mandatory_attrs_per_std_name,
            "1_meta.Mandatory_attributes_per_standardname",
        )

    def test_mandatory_attributes_per_standardname_ko(
        self, ds_lat_var_without_bounds_attr
    ):
        self._check_failure(
            ds_lat_var_without_bounds_attr,
            "1_meta.Mandatory_attributes_per_standardname",
        )

    def test_mandatory_attributes_values_ok(self, ds_with_mandatory_attr_values):
        self._check_success(
            ds_with_mandatory_attr_values, "1_meta.Mandatory_attributes_content"
        )

    def test_mandatory_attributes_values_ko(self, ds_with_bad_mandatory_attr_values):
        self._check_failure(
            ds_with_bad_mandatory_attr_values, "1_meta.Mandatory_attributes_content"
        )

    def test_mandatory_attributes_values_per_variable_ok(
        self, ds_with_mandatory_attributes_per_variable_name
    ):
        self._check_success(
            ds_with_mandatory_attributes_per_variable_name,
            "1_meta.Mandatory_attributes_values_per_variablename",
        )

    def test_mandatory_attributes_values_per_variable_ko(
        self, ds_without_mandatory_attributes_per_variable_name
    ):
        self._check_failure(
            ds_without_mandatory_attributes_per_variable_name,
            "1_meta.Mandatory_attributes_values_per_variablename",
        )

    def test_mandatory_dimensions_per_var_name_ok(
        self, ds_with_mandatory_attributes_per_variable_name
    ):
        self._check_success(
            ds_with_mandatory_attributes_per_variable_name,
            "1_meta.Mandatory_dimensions_per_variablename",
        )

    def test_mandatory_dimensions_per_var_name_ko(
        self, ds_without_mandatory_dim_for_variable
    ):
        self._check_failure(
            ds_without_mandatory_dim_for_variable,
            "1_meta.Mandatory_dimensions_per_variablename",
        )

    def test_mandatory_attributes_per_var_name_ok(
        self, ds_with_mandatory_attributes_per_variable_name
    ):
        self._check_success(
            ds_with_mandatory_attributes_per_variable_name,
            "1_meta.Mandatory_attributes_per_variablename",
        )

    def test_mandatory_attributes_per_var_name_ko(
        self, ds_without_mandatory_attributes_per_variable_name
    ):
        self._check_failure(
            ds_without_mandatory_attributes_per_variable_name,
            "1_meta.Mandatory_attributes_per_variablename",
        )

    def test_mandatory_global_attrs_values_ok(
        self, ds_with_all_mandatory_global_attr_content
    ):
        self._check_success(
            ds_with_all_mandatory_global_attr_content,
            "1_meta.Mandatory_global_attributes_content",
        )

    def test_mandatory_global_attrs_values_ko(
        self, ds_with_mandatory_global_attr_content_bad_value
    ):
        self._check_failure(
            ds_with_mandatory_global_attr_content_bad_value,
            "1_meta.Mandatory_global_attributes_content",
        )

    def test_mandatory_global_attrs_ok(self, ds_with_all_global_mandatory_attrs):
        self._check_success(
            ds_with_all_global_mandatory_attrs, "1_meta.Mandatory_global_attributes"
        )

    def test_mandatory_global_attrs_ko(self, ds_with_all_mandatory_global_attr_content):
        self._check_failure(
            ds_with_all_mandatory_global_attr_content,
            "1_meta.Mandatory_global_attributes",
        )

    def test_mandatory_global_attrs_content_list_ok(
        self, ds_with_all_mandatory_global_attr_content
    ):
        self._check_success(
            ds_with_all_mandatory_global_attr_content,
            "1_meta.Mandatory_global_attributes_content_list",
        )

    def test_mandatory_global_attrs_content_list_ko(
        self, ds_with_missing_val_in_kw_global_attr
    ):
        self._check_failure(
            ds_with_missing_val_in_kw_global_attr,
            "1_meta.Mandatory_global_attributes_content_list",
        )

    def test_mandatory_global_attrs_content_date_ok(
        self, ds_with_all_global_mandatory_attrs
    ):
        self._check_success(
            ds_with_all_mandatory_global_attr_content,
            "1_meta.Mandatory_global_attributes_content_date",
        )

    def test_mandatory_global_attrs_content_date_ko(
        self, ds_with_bad_date_content_in_global_attrs
    ):
        self._check_failure(
            ds_with_bad_date_content_in_global_attrs,
            "1_meta.Mandatory_global_attributes_content_date",
        )

    def test_mandatory_global_attrs_content_pattern_ok(
        self, ds_with_all_global_mandatory_attrs
    ):
        self._check_success(
            ds_with_all_global_mandatory_attrs,
            "1_meta.Mandatory_global_attributes_content_pattern",
        )

    def test_mandatory_global_attrs_content_pattern_ko(
        self, ds_with_bad_date_content_in_global_attrs
    ):
        self._check_failure(
            ds_with_bad_date_content_in_global_attrs,
            "1_meta.Mandatory_global_attributes_content_pattern",
        )

    def test_mandatory_grib_consistency_ok(self, ds_with_specific_humidity):
        self._check_success(
            ds_with_specific_humidity, "1_meta.Mandatory_gribconsistency"
        )

    def test_mandatory_grib_consistency_ko(self, ds_with_specific_humidity_malformed):
        self._check_failure(
            ds_with_specific_humidity_malformed, "1_meta.Mandatory_gribconsistency"
        )

    def _check_success(self, dataset, check):
        checker = self._get_checker(dataset, check)
        self._check_and_assert_status(checker, 1)
        assert all("error" not in line.lower() for line in checker.messages)

    def _check_failure(self, dataset, check):
        checker = self._get_checker(dataset, check)
        self._check_and_assert_status(checker, 0)
        assert any("error" in line.lower() for line in checker.messages)

    @staticmethod
    def _check_and_assert_status(checker, status):
        checker.cp_check_compliance()
        assert checker.status == status

    @staticmethod
    def _get_checker(ds, check):
        return Cpchecker(ds, c3stype=CHECK_TYPE, checks=check, passedcheckinfo=True)
