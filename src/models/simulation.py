"""The top-level configuration and run record: one experiment as a whole."""

from pydantic import Field, model_validator

from models.base import StrictModel
from models.detector import Detector
from models.metadata import Metadata
from models.environment import WorkingEnvironment
from models.run import RunSettings
from models.sample import Sample
from models.shielding import Shielding
from models.source import Source


class Simulation(StrictModel):
    """Top-level GRAACE-SIM configuration and run record.

    A flat composition of the parts of one experiment. ``source``,
    ``detectors``, ``run``, and ``metadata`` are required. ``sample`` is optional
    (a setup may have no sample), ``shielding`` defaults to an empty list, and
    ``environment`` defaults to a run named ``example`` under ``data/``.
    """

    source: Source
    sample: Sample | None = None
    detectors: list[Detector]
    shielding: list[Shielding] = Field(default_factory=list)
    run: RunSettings
    metadata: Metadata
    environment: WorkingEnvironment = Field(default_factory=WorkingEnvironment)

    @model_validator(mode="after")
    def unique_detector_names(self) -> "Simulation":
        """Each detector name becomes a directory and a detector volume, so two
        detectors sharing a name would collide. Require the names to be unique."""
        names = [detector.name for detector in self.detectors]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            raise ValueError(f"detector names must be unique; repeated: {duplicates}")
        return self
