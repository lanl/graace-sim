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
    # The fraction of the machine's CPU cores a run may use. The macro writer
    # turns this into the engine's thread count, so a run never takes more of the
    # machine than this allows. Defaults below 100 so a run leaves the machine
    # responsive by default; set it to 100 to use every core.
    cpu_percent: int = Field(default=80, ge=1, le=100)

    @field_validator("binary")
    @classmethod
    def non_blank_binary(cls, value: str) -> str:
        """Reject a blank or whitespace-only binary name."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("`runner.binary` must not be blank.")
        return normalized
