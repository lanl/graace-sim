"""The runner wiring (not the physics): it builds the command from the resolved
binary and the written macro, streams output to `logs/run.log`, raises on a
nonzero exit or a missing binary, and verifies each detector's results."""

from pathlib import Path

import pytest

from config.yaml_io import load_simulation
from models.simulation import Simulation
from runner import run_simulation as runner

EXAMPLE = Path(__file__).parents[2] / "examples" / "yaml_files" / "example.yaml"


class FakeProcess:
    """A stand-in for ``subprocess.Popen``: yields the given lines, then exits
    with ``return_code``. ``on_wait`` runs when the process is waited on, so a
    test can mimic the engine writing its results."""

    def __init__(self, lines, return_code=0, on_wait=None):
        self.stdout = iter(lines)
        self._return_code = return_code
        self._on_wait = on_wait

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def wait(self):
        if self._on_wait is not None:
            self._on_wait()
        return self._return_code


def _config(tmp_path: Path) -> Simulation:
    """The example config with its run directory redirected under tmp_path."""
    config = load_simulation(EXAMPLE)
    config.environment.working_directory = tmp_path
    return config


def _write_results(config: Simulation) -> None:
    """Create one Parquet file per detector, as the engine would during a run."""
    for detector in config.detectors:
        directory = config.environment.results_directory / detector.name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "gamma_hits-part-00000.parquet").write_bytes(b"")


def _install_engine(monkeypatch, popen) -> list[list[str]]:
    """Put a fake engine on PATH and a fake Popen in place; record commands."""
    monkeypatch.setattr(runner.shutil, "which", lambda name: f"/fake/bin/{name}")
    commands: list[list[str]] = []

    def fake_popen(command, *args, **kwargs):
        commands.append(command)
        return popen()

    monkeypatch.setattr(runner.subprocess, "Popen", fake_popen)
    return commands


def test_builds_command_from_resolved_binary_and_macro(tmp_path, monkeypatch):
    config = _config(tmp_path)
    lines = ["  ... processed 1000 events\n", "Run finished\n"]
    commands = _install_engine(
        monkeypatch, lambda: FakeProcess(lines, on_wait=lambda: _write_results(config))
    )

    run_dir = runner.run_simulation(config)

    assert run_dir == config.environment.run_directory
    assert commands == [["/fake/bin/graace-sim", str(config.environment.macro_file)]]


def test_writes_run_log_from_streamed_output(tmp_path, monkeypatch):
    config = _config(tmp_path)
    lines = ["  ... processed 1000 events\n", "SimIO: wrote 5 gamma hits\n"]
    _install_engine(
        monkeypatch, lambda: FakeProcess(lines, on_wait=lambda: _write_results(config))
    )

    runner.run_simulation(config)

    log = (config.environment.log_directory / "run.log").read_text()
    assert log == "".join(lines)


def test_nonzero_exit_raises(tmp_path, monkeypatch):
    config = _config(tmp_path)
    _install_engine(monkeypatch, lambda: FakeProcess(["boom\n"], return_code=1))

    with pytest.raises(RuntimeError, match="exited with code 1"):
        runner.run_simulation(config)


def test_binary_not_on_path_raises_before_launch(tmp_path, monkeypatch):
    config = _config(tmp_path)
    monkeypatch.setattr(runner.shutil, "which", lambda name: None)

    def fail_popen(*args, **kwargs):  # pragma: no cover - must not be reached
        raise AssertionError("engine was launched despite not being on PATH")

    monkeypatch.setattr(runner.subprocess, "Popen", fail_popen)

    with pytest.raises(FileNotFoundError, match="not on PATH"):
        runner.run_simulation(config)


def test_verify_output_raises_when_results_missing(tmp_path, monkeypatch):
    config = _config(tmp_path)
    # No on_wait, so the fake engine leaves the results directories empty.
    _install_engine(monkeypatch, lambda: FakeProcess(["done\n"]))

    with pytest.raises(FileNotFoundError, match="no results were written"):
        runner.run_simulation(config)


def test_verify_output_passes_when_results_present(tmp_path, monkeypatch):
    config = _config(tmp_path)
    _install_engine(
        monkeypatch, lambda: FakeProcess(["done\n"], on_wait=lambda: _write_results(config))
    )

    # Should not raise.
    runner.run_simulation(config)


def test_show_progress_off_skips_progress_but_still_runs(tmp_path, monkeypatch):
    config = _config(tmp_path)
    config.runner.show_progress = False
    _install_engine(
        monkeypatch,
        lambda: FakeProcess(
            ["  ... processed 1000 events\n"], on_wait=lambda: _write_results(config)
        ),
    )

    run_dir = runner.run_simulation(config)
    assert run_dir == config.environment.run_directory
