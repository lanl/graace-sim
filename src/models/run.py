"""How the engine runs: how many neutrons to simulate and the random seed."""

from pydantic import Field

from models.base import StrictModel


class RunSettings(StrictModel):
    """Run controls: neutron count and random seed."""

    neutrons: int = Field(gt=0)
    seed: int = Field(default=0, ge=0)
