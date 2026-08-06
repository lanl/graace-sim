"""The top-level configuration and run record: one experiment as a whole."""

from pydantic import Field

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
    shielding: list[Shielding] = []
    run: RunSettings
    metadata: Metadata
    environment: WorkingEnvironment = Field(default_factory=WorkingEnvironment)
