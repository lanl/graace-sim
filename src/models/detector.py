"""One gamma detector: its type, position, dimensions, and energy resolution."""

from pydantic import Field

from models.base import StrictModel
from models.vectors import Size3Mm, Vec3Mm


class Detector(StrictModel):
    """A single gamma detector. A simulation may hold more than one."""

    type: str = Field(min_length=1)
    position_mm: Vec3Mm
    dimension_mm: Size3Mm
    energy_resolution_kev: float | None = Field(default=None, gt=0)
