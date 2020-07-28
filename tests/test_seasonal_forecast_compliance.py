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
def ds_2_dimensions(dataset_with_valid_file_format):
    dataset_with_valid_file_format.createDimension("lon", 360)
    dataset_with_valid_file_format.createDimension("lat", 181)
    yield dataset_with_valid_file_format


@pytest.fixture
def ds_one_var_2_dimensions(ds_2_dimensions):
    ds_2_dimensions.createVariable("foo", np.float, ("lon", "lat"))
    yield ds_2_dimensions


@pytest.fixture
def ds_2_vars_2_dimensions(ds_one_var_2_dimensions):
    ds_one_var_2_dimensions.createVariable("bar", np.float, ("lon", "lat"))
    yield ds_one_var_2_dimensions


class TestC3S01:
    CONVENTION = "CF-1.6 C3S-0.1"

    @staticmethod
    def _get_checker(ds, check):
        return Cpchecker(ds, c3stype=CHECK_TYPE, checks=check)

    def test_meta_mandatory_cf_convention_ok(self, dataset_with_valid_file_format):
        dataset_with_valid_file_format.setncattr("convention", self.CONVENTION)
        cp_check = self._get_checker(
            dataset_with_valid_file_format, "1_meta.1_submeta.Mandatory_cf_convention"
        )
        # Check passes
        cp_check.cp_check_compliance()
        assert cp_check.status == 1

    def test_meta_mandatory_cf_convention_ko(self, dataset_with_valid_file_format):
        # First case: Invalid string for one of the bits
        dataset_with_valid_file_format.setncattr("convention", "CF-1.6 C3S-1")
        cp_check = self._get_checker(
            dataset_with_valid_file_format, "1_meta.1_submeta.Mandatory_cf_convention"
        )
        # Check fails
        cp_check.cp_check_compliance()
        assert cp_check.status == 0

        # Second case: Inverted order of the valid bits
        reversed_convention = " ".join(reversed(self.CONVENTION.split()))
        dataset_with_valid_file_format.setncattr("convention", reversed_convention)
        cp_check = self._get_checker(
            dataset_with_valid_file_format, "1_meta.1_submeta.Mandatory_cf_convention"
        )
        # Check fails
        cp_check.cp_check_compliance()
        assert cp_check.status == 0

    def test_mandatory_netcdf_format_ok(self, dataset_with_valid_file_format):
        cp_check = self._get_checker(
            dataset_with_valid_file_format, "1_meta.Mandatory_netcdf_format"
        )
        # Check succeeds
        cp_check.cp_check_compliance()
        assert cp_check.status == 1

    def test_mandatory_netcdf_format_ko(self, dataset_with_invalid_file_format):
        cp_check = self._get_checker(
            dataset_with_invalid_file_format, "1_meta.Mandatory_netcdf_format"
        )
        # Check fails
        cp_check.cp_check_compliance()
        assert cp_check.status == 0

    def test_mandatory_number_datavariable_per_netcdf_ok(self, ds_one_var_2_dimensions):
        cp_check = self._get_checker(
            ds_one_var_2_dimensions, "1_meta.Mandatory_number_datavariable_per_netcdf"
        )
        # Check succeeds
        cp_check.cp_check_compliance()
        assert cp_check.status == 1

    def test_mandatory_number_datavariable_per_netcdf_ko(self, ds_2_vars_2_dimensions):
        cp_check = self._get_checker(
            ds_2_vars_2_dimensions, "1_meta.Mandatory_number_datavariable_per_netcdf"
        )
        # Check fails
        cp_check.cp_check_compliance()
        assert cp_check.status == 0
