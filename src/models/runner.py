"""How to launch the engine: the binary name and launch options.

Separate from ``RunSettings`` (``run``), which is the physics of the run (neutron
count and seed). This model is only about invoking the compiled engine.
"""

from pydantic import Field, field_validator

from models.base import StrictModel


class SimRunner(StrictModel):
    """Engine launch settings for one simulation run."""

    binary: str = Field(default="graace-sim", min_length=1)
    show_progress: bool = Field(default=True)
    verify_output: bool = Field(default=True)

    @field_validator("binary")
    @classmethod
    def non_blank_binary(cls, value: str) -> str:
        """Reject a blank or whitespace-only binary name."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("`runner.binary` must not be blank.")
        return normalized
