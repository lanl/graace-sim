"""One gamma detector: its name, type, position, dimensions, and energy resolution."""

from pydantic import Field, field_validator

from models.base import StrictModel, check_directory_safe_name
from models.vectors import Size3Mm, Vec3Mm


class Detector(StrictModel):
    """A single gamma detector. A simulation may hold more than one."""

    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    position_mm: Vec3Mm
    dimension_mm: Size3Mm
    energy_resolution_kev: float | None = Field(default=None, gt=0)

    @field_validator("name")
    @classmethod
    def safe_name(cls, name: str) -> str:
        """The name labels the detector's output directory, so reject path
        separators and `.`/`..`."""
        return check_directory_safe_name(name, "name")
