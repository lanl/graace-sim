"""The SimRunner launch settings: sensible defaults, a non-blank binary, and a
default SimRunner on any Simulation with no `runner` block."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from config.yaml_io import load_simulation
from models.runner import SimRunner

EXAMPLE = Path(__file__).parents[2] / "examples" / "yaml_files" / "example.yaml"


def test_defaults():
    runner = SimRunner()
    assert runner.binary == "graace-sim"
    assert runner.show_progress is True
    assert runner.verify_output is True
    # Below 100 so a run leaves the machine responsive by default.
    assert runner.cpu_percent == 80


@pytest.mark.parametrize("bad_percent", [0, -1, 101, 200])
def test_cpu_percent_out_of_range_is_rejected(bad_percent):
    with pytest.raises(ValidationError):
        SimRunner(cpu_percent=bad_percent)


@pytest.mark.parametrize("good_percent", [1, 50, 100])
def test_cpu_percent_in_range_is_accepted(good_percent):
    assert SimRunner(cpu_percent=good_percent).cpu_percent == good_percent


@pytest.mark.parametrize("bad_binary", ["", "   ", "\t"])
def test_blank_binary_is_rejected(bad_binary):
    with pytest.raises(ValidationError):
        SimRunner(binary=bad_binary)


def test_binary_is_stripped():
    assert SimRunner(binary="  graace-sim  ").binary == "graace-sim"


def test_simulation_without_runner_block_gets_default():
    # The example config has no `runner:` block, so it should get the default.
    simulation = load_simulation(EXAMPLE)
    assert simulation.runner == SimRunner()
