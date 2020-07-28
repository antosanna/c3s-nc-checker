"""Unit tests for C3S Seasonal Forecast Checking"""
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
