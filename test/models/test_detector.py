"""Detector name rules: a name must be directory-safe, and detector names must
be unique within a simulation (each becomes a directory and a detector volume)."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from config.yaml_io import load_simulation
from models.detector import Detector
from models.vectors import Size3Mm, Vec3Mm

EXAMPLE = Path(__file__).parents[2] / "examples" / "yaml_files" / "example.yaml"

POSITION = Vec3Mm(x_mm=0, y_mm=80, z_mm=0)
DIMENSION = Size3Mm(x_mm=60, y_mm=60, z_mm=50)


def test_name_is_required():
    with pytest.raises(ValidationError):
        Detector(type="HPGe", position_mm=POSITION, dimension_mm=DIMENSION)


@pytest.mark.parametrize("bad_name", ["hpge/top", "hpge\\top", ".", ".."])
def test_unsafe_name_is_rejected(bad_name):
    with pytest.raises(ValidationError) as info:
        Detector(
            name=bad_name, type="HPGe", position_mm=POSITION, dimension_mm=DIMENSION
        )
    assert "name" in str(info.value)


def test_duplicate_detector_names_are_rejected():
    simulation = load_simulation(EXAMPLE)
    second = simulation.detectors[0].model_copy(deep=True)  # same name
    with pytest.raises(ValidationError) as info:
        simulation.detectors = [simulation.detectors[0], second]
    assert "unique" in str(info.value)


def test_distinct_detector_names_pass():
    simulation = load_simulation(EXAMPLE)
    second = simulation.detectors[0].model_copy(deep=True)
    second.name = "hpge_bottom"
    simulation.detectors = [simulation.detectors[0], second]
    assert [d.name for d in simulation.detectors] == ["hpge", "hpge_bottom"]
