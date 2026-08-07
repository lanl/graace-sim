"""Sample composition rules: known symbols, fraction sum, duplicates, tolerance."""

import pytest
from pydantic import ValidationError

from models.sample import (
    COMPOSITION_TOLERANCE,
    Sample,
    SampleComposition,
    SampleElement,
    SampleIsotope,
)
from models.vectors import Vec3Mm

ORIGIN = Vec3Mm(x_mm=0, y_mm=0, z_mm=0)


def test_unknown_symbol_is_rejected():
    with pytest.raises(ValidationError):
        SampleElement(symbol="Xx", mass_fraction=1.0)


def test_fractions_summing_to_one_pass():
    SampleComposition(
        density_g_cm3=1.0,
        elements=[
            SampleElement(symbol="Fe", mass_fraction=0.7),
            SampleElement(symbol="C", mass_fraction=0.3),
        ],
    )


def test_wrong_sum_is_rejected():
    with pytest.raises(ValidationError) as info:
        SampleComposition(
            density_g_cm3=1.0,
            elements=[SampleElement(symbol="Fe", mass_fraction=0.5)],
        )
    assert "sum to 1.0" in str(info.value)


def test_duplicate_symbol_is_rejected():
    with pytest.raises(ValidationError) as info:
        SampleComposition(
            density_g_cm3=1.0,
            elements=[
                SampleElement(symbol="Fe", mass_fraction=0.5),
                SampleElement(symbol="Fe", mass_fraction=0.5),
            ],
        )
    assert "duplicate element symbol" in str(info.value)


def test_sum_within_tolerance_passes():
    off = COMPOSITION_TOLERANCE / 2
    SampleComposition(
        density_g_cm3=1.0,
        elements=[
            SampleElement(symbol="Fe", mass_fraction=0.5 + off),
            SampleElement(symbol="C", mass_fraction=0.5),
        ],
    )


def test_isotopes_default_to_none():
    element = SampleElement(symbol="Fe", mass_fraction=1.0)
    assert element.isotopes is None


def test_isotope_atom_fractions_summing_to_one_pass():
    SampleElement(
        symbol="U",
        mass_fraction=1.0,
        isotopes=[
            SampleIsotope(mass_number=235, atom_fraction=0.9),
            SampleIsotope(mass_number=238, atom_fraction=0.1),
        ],
    )


def test_isotope_wrong_sum_is_rejected():
    with pytest.raises(ValidationError) as info:
        SampleElement(
            symbol="U",
            mass_fraction=1.0,
            isotopes=[SampleIsotope(mass_number=235, atom_fraction=0.5)],
        )
    assert "sum to 1.0" in str(info.value)


def test_duplicate_mass_number_is_rejected():
    with pytest.raises(ValidationError) as info:
        SampleElement(
            symbol="U",
            mass_fraction=1.0,
            isotopes=[
                SampleIsotope(mass_number=235, atom_fraction=0.5),
                SampleIsotope(mass_number=235, atom_fraction=0.5),
            ],
        )
    assert "duplicate isotope mass number" in str(info.value)


def test_empty_isotope_list_is_rejected():
    with pytest.raises(ValidationError):
        SampleElement(symbol="U", mass_fraction=1.0, isotopes=[])


def test_cylinder_requires_height():
    composition = SampleComposition(
        density_g_cm3=7.87,
        elements=[SampleElement(symbol="Fe", mass_fraction=1.0)],
    )
    Sample(
        composition=composition,
        shape="cylinder",
        size_mm=10,
        height_mm=20,
        position_mm=ORIGIN,
    )
    with pytest.raises(ValidationError) as info:
        Sample(
            composition=composition,
            shape="cylinder",
            size_mm=10,
            position_mm=ORIGIN,
        )
    assert "sample.height_mm" in str(info.value)
