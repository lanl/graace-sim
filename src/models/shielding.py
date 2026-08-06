"""An optional shielding block: material, thickness, and placement."""

from pydantic import Field

from models.base import StrictModel
from models.vectors import Vec3Mm


class Shielding(StrictModel):
    """One shielding block. A simulation may hold none, one, or several."""

    material: str = Field(min_length=1)
    thickness_mm: float = Field(gt=0)
    position_mm: Vec3Mm
