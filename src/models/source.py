"""The neutron source: its particle, position, energy, and timing."""

from typing import Literal

from pydantic import Field, model_validator

from models.base import StrictModel
from models.vectors import Vec3Mm


class SourcePosition(StrictModel):
    """Where the neutrons originate and the emission shape.

    A ``radius_mm`` is required only for shapes that need one, so it is optional
    at the schema level and enforced by an after-validator.
    """

    shape: Literal["point", "disk", "beam"] = "point"
    center_mm: Vec3Mm
    radius_mm: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def check_radius(self) -> "SourcePosition":
        if self.shape in {"disk", "beam"} and self.radius_mm is None:
            raise ValueError("`source.position.radius_mm` is required for shape 'disk' or 'beam'.")
        return self


class SourceEnergy(StrictModel):
    """The neutron energy: a single value, or a spectrum read from a file.

    Which field is required depends on ``type``, so both are optional at the
    schema level and an after-validator enforces the one the chosen type needs.
    """

    type: Literal["mono", "spectrum"] = "mono"
    mono_mev: float | None = Field(default=None, gt=0)
    spectrum_file: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def check_energy(self) -> "SourceEnergy":
        if self.type == "mono" and self.mono_mev is None:
            raise ValueError("`source.energy.mono_mev` is required when type is 'mono'.")
        if self.type == "spectrum" and self.spectrum_file is None:
            raise ValueError("`source.energy.spectrum_file` is required when type is 'spectrum'.")
        return self


class SourceTiming(StrictModel):
    """The time structure of the source: continuous, a single pulse, or periodic.

    Which fields are required depends on ``mode``, so they are optional at the
    schema level and an after-validator enforces the ones each mode needs.
    """

    mode: Literal["continuous", "single", "periodic"] = "continuous"
    pulse_width_ns: float | None = Field(default=None, gt=0)
    pulse_period_ns: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def check_timing(self) -> "SourceTiming":
        if self.mode in {"single", "periodic"} and self.pulse_width_ns is None:
            raise ValueError("`source.timing.pulse_width_ns` is required for mode 'single' or 'periodic'.")
        if self.mode == "periodic" and self.pulse_period_ns is None:
            raise ValueError("`source.timing.pulse_period_ns` is required for mode 'periodic'.")
        return self


class Source(StrictModel):
    """The neutron source, composed of its position, energy, and timing parts."""

    particle: str = Field(default="neutron", min_length=1)
    position: SourcePosition
    energy: SourceEnergy
    timing: SourceTiming = Field(default_factory=SourceTiming)
