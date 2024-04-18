"""Unit tests for C3S Seasonal Forecast Checking"""
CHECK_TYPE = "seasonal"


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
            ds_with_all_global_mandatory_attrs,
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

    def test_mandatory_data_intervals_ok(self, ds_with_good_data_intervals):
        self._check_success(
            ds_with_good_data_intervals, "2_data.Mandatory_data_intervals"
        )

    def test_mandatory_data_intervals_ko(self, ds_with_bad_data_intervals):
        self._check_failure(
            ds_with_bad_data_intervals, "2_data.Mandatory_data_intervals"
        )

    def test_mandatory_data_min_max_ok(self, ds_with_good_data_min_max):
        self._check_success(ds_with_good_data_min_max, "2_data.Mandatory_data_minmax")

    def test_mandatory_data_min_max_ko(self, ds_with_bad_data_min_max):
        self._check_failure(ds_with_bad_data_min_max, "2_data.Mandatory_data_minmax")

    def test_mandatory_data_ranges_ok(self, ds_with_good_data_min_max):
        self._check_success(ds_with_good_data_min_max, "2_data.Mandatory_data_ranges")

    def test_mandatory_data_ranges_ko(self, ds_with_bad_data_min_max):
        self._check_failure(ds_with_bad_data_min_max, "2_data.Mandatory_data_ranges")

    def test_mandatory_data_values_ok(self, ds_with_good_data_min_max):
        self._check_success(ds_with_good_data_min_max, "2_data.Mandatory_data_values")

    def test_mandatory_data_values_ko(self, ds_with_bad_data_min_max):
        self._check_failure(ds_with_bad_data_min_max, "2_data.Mandatory_data_values")

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
        assert False

    @staticmethod
    def _get_checker(ds, check):
        return None
