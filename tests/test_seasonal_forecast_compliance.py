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

    def _check_success(self, dataset, check):
        checker = self._get_checker(dataset, check)
        self._check_and_assert_status(checker, 1)

    def _check_failure(self, dataset, check):
        checker = self._get_checker(dataset, check)
        self._check_and_assert_status(checker, 0)

    @staticmethod
    def _check_and_assert_status(checker, status):
        checker.cp_check_compliance()
        assert checker.status == status

    @staticmethod
    def _get_checker(ds, check):
        return Cpchecker(ds, c3stype=CHECK_TYPE, checks=check)
