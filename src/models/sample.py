"""The assayed material: its composition, density, shape, size, and position."""

import math
from typing import Literal

from pydantic import Field, field_validator, model_validator

from models.base import StrictModel
from models.vectors import Vec3Mm

# Every chemical element symbol, hydrogen through oganesson.
CHEMICAL_ELEMENT_SYMBOLS = frozenset({
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr",
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
    "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",
    "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
    "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
    "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm",
    "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds",
    "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og",
})

# How close the element mass fractions must sum to 1.0.
COMPOSITION_TOLERANCE = 1.0e-6


class SampleIsotope(StrictModel):
    """One isotope of an element, as an atom fraction of that element."""

    mass_number: int = Field(gt=0)
    atom_fraction: float = Field(gt=0.0, le=1.0)


class SampleElement(StrictModel):
    """One element in the sample, as a mass fraction of the whole.

    ``isotopes`` is an optional atom-fraction breakdown for this element. ``None``
    (the default) uses natural isotopic abundances. When given, the atom fractions
    must sum to 1.0 and mass numbers must be unique.
    """

    symbol: str
    mass_fraction: float = Field(gt=0.0, le=1.0)
    isotopes: list[SampleIsotope] | None = Field(default=None, min_length=1)

    @field_validator("symbol")
    @classmethod
    def known_element(cls, symbol: str) -> str:
        if symbol not in CHEMICAL_ELEMENT_SYMBOLS:
            raise ValueError(f"unknown chemical element symbol: {symbol!r}")
        return symbol

    @model_validator(mode="after")
    def check_isotopes(self) -> "SampleElement":
        if self.isotopes is None:
            return self
        mass_numbers = [isotope.mass_number for isotope in self.isotopes]
        if len(mass_numbers) != len(set(mass_numbers)):
            raise ValueError(f"duplicate isotope mass number in element {self.symbol!r}")
        total = sum(isotope.atom_fraction for isotope in self.isotopes)
        if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=COMPOSITION_TOLERANCE):
            raise ValueError(
                f"isotope atom fractions for element {self.symbol!r} must sum to 1.0"
            )
        return self


class SampleComposition(StrictModel):
    """The material makeup: density and element mass fractions summing to 1.0."""

    density_g_cm3: float = Field(gt=0)
    elements: list[SampleElement] = Field(min_length=1)

    @model_validator(mode="after")
    def check_fractions(self) -> "SampleComposition":
        symbols = [e.symbol for e in self.elements]
        if len(symbols) != len(set(symbols)):
            raise ValueError("duplicate element symbol")
        total = sum(e.mass_fraction for e in self.elements)
        if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=COMPOSITION_TOLERANCE):
            raise ValueError("element mass fractions must sum to 1.0")
        return self


class Sample(StrictModel):
    """The assayed material: what it is made of, its shape, size, and placement.

    ``size_mm`` is the cube side or the sphere/cylinder radius. ``height_mm`` is
    the cylinder height and is required only for a cylinder, so it is optional at
    the schema level and enforced by an after-validator.
    """

    composition: SampleComposition
    shape: Literal["cube", "sphere", "cylinder"] = "cylinder"
    size_mm: float = Field(gt=0)
    height_mm: float | None = Field(default=None, gt=0)
    position_mm: Vec3Mm

    @model_validator(mode="after")
    def check_height(self) -> "Sample":
        if self.shape == "cylinder" and self.height_mm is None:
            raise ValueError("`sample.height_mm` is required for shape 'cylinder'.")
        return self
