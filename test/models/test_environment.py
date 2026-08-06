"""WorkingEnvironment computes the run layout without touching the filesystem."""

from pathlib import Path

from models.environment import WorkingEnvironment


def test_default_layout():
    paths = WorkingEnvironment()
    assert paths.run_directory == Path("data/example_000")
    assert paths.log_directory == Path("data/example_000/logs")
    assert paths.results_directory == Path("data/example_000/results")
    assert paths.macro_file == Path("data/example_000/example.mac")


def test_custom_working_directory_and_sub_run():
    paths = WorkingEnvironment(working_directory="runs", run_id="assay", sub_run=7)
    assert paths.run_directory == Path("runs/assay_007")
    assert paths.log_directory == Path("runs/assay_007/logs")
    assert paths.results_directory == Path("runs/assay_007/results")
    assert paths.macro_file == Path("runs/assay_007/assay.mac")


def test_paths_do_not_create_directories(tmp_path):
    paths = WorkingEnvironment(working_directory=tmp_path, run_id="run", sub_run=1)
    # Accessing the properties must not create anything on disk.
    _ = (paths.run_directory, paths.log_directory, paths.results_directory)
    assert not paths.run_directory.exists()
