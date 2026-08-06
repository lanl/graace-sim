"""The YAML loader: the example round-trips; a broken copy raises."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from config.yaml_io import load_simulation
from models.simulation import Simulation

EXAMPLE = Path(__file__).parents[2] / "examples" / "yaml_files" / "example.yaml"


def test_example_loads_into_simulation():
    simulation = load_simulation(EXAMPLE)
    assert isinstance(simulation, Simulation)
    assert simulation.source.energy.mono_mev == 14.1
    assert simulation.environment.run_directory == Path("data/example_000")


def test_broken_copy_raises(tmp_path):
    data = yaml.safe_load(EXAMPLE.read_text())
    data["run"]["neutrons"] = -1  # must be > 0
    broken = tmp_path / "broken.yaml"
    broken.write_text(yaml.safe_dump(data))
    with pytest.raises(ValidationError) as info:
        load_simulation(broken)
    assert "neutrons" in str(info.value)
