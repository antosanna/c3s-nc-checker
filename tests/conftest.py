import pytest

from netCDF4 import Dataset

from c3schecker.checks import ChecksRegistry


@pytest.fixture
def empty_dataset(tmpdir):
    file_path = tmpdir / "dataset.nc"
    # First write the dataset to disk
    Dataset(file_path, mode="w").close()
    # Then open it again for reading
    ds = Dataset(file_path)
    yield ds
    # Tear it down
    ds.close()


@pytest.fixture
def input_file(empty_dataset):
    return empty_dataset.filepath()


@pytest.fixture
def spec():
    return {"convention": "C3S-0.1", "constraints": {}}


@pytest.fixture(params=[("dumb_passing_check", lambda x, y: {"status": 1})])
def good_check(request, monkeypatch, spec):
    check_name, check_function = request.param
    monkeypatch.setitem(
        ChecksRegistry()[spec["convention"]], check_name, check_function
    )
    return check_name


@pytest.fixture(
    params=[
        ("dumb_failing_check", lambda x, y: {"status": 0, "errors": ["Not Okay :("]})
    ]
)
def bad_check(request, monkeypatch, spec):
    check_name, check_function = request.param
    monkeypatch.setitem(
        ChecksRegistry()[spec["convention"]], check_name, check_function
    )
    return check_name
