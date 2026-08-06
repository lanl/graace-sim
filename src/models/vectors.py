"""Small reusable vectors shared among the models: a position and a size, both in millimeters."""

from pydantic import Field

from models.base import StrictModel


class Vec3Mm(StrictModel):
    """A 3D position in millimeters. Any sign allowed."""

    x_mm: float
    y_mm: float
    z_mm: float


class Size3Mm(StrictModel):
    """A 3D size in millimeters. Every side must be positive."""

    x_mm: float = Field(gt=0)
    y_mm: float = Field(gt=0)
    z_mm: float = Field(gt=0)
