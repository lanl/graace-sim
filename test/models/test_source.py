"""The source conditional-required validators, keyed off shape / type / mode."""

import pytest
from pydantic import ValidationError

from models.source import SourceEnergy, SourcePosition, SourceTiming
from models.vectors import Vec3Mm

CENTER = Vec3Mm(x_mm=0, y_mm=0, z_mm=0)


def test_position_point_needs_no_radius():
    SourcePosition(shape="point", center_mm=CENTER)


def test_position_disk_requires_radius():
    with pytest.raises(ValidationError) as info:
        SourcePosition(shape="disk", center_mm=CENTER)
    assert "source.position.radius_mm" in str(info.value)


def test_energy_mono_requires_mono_mev():
    SourceEnergy(type="mono", mono_mev=14.1)
    with pytest.raises(ValidationError) as info:
        SourceEnergy(type="mono")
    assert "source.energy.mono_mev" in str(info.value)


def test_energy_spectrum_requires_spectrum_file():
    SourceEnergy(type="spectrum", spectrum_file="cf252.txt")
    with pytest.raises(ValidationError) as info:
        SourceEnergy(type="spectrum")
    assert "source.energy.spectrum_file" in str(info.value)


def test_timing_continuous_needs_no_fields():
    SourceTiming(mode="continuous")


def test_timing_single_requires_pulse_width():
    SourceTiming(mode="single", pulse_width_ns=5.0)
    with pytest.raises(ValidationError) as info:
        SourceTiming(mode="single")
    assert "source.timing.pulse_width_ns" in str(info.value)


def test_timing_periodic_requires_period():
    SourceTiming(mode="periodic", pulse_width_ns=5.0, pulse_period_ns=100.0)
    with pytest.raises(ValidationError) as info:
        SourceTiming(mode="periodic", pulse_width_ns=5.0)
    assert "source.timing.pulse_period_ns" in str(info.value)
