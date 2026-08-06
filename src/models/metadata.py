"""Bookkeeping and the run's identity, including where output goes."""

from pathlib import Path

from pydantic import Field

from models.base import StrictModel


class Metadata(StrictModel):
    """Author, date, description, run identity, and the output location."""

    author: str = Field(min_length=1)
    date: str = Field(min_length=1)
    description: str = Field(min_length=1)
    run_id: str = Field(default="example", min_length=1)
    sub_run: int = Field(default=0, ge=0, le=9999)
    output_directory: str = Field(default="data", min_length=1)

    @property
    def run_directory(self) -> Path:
        """The run's output directory: ``<output_directory>/<run_id>_<NNN>``."""
        return Path(self.output_directory) / f"{self.run_id}_{self.sub_run:03d}"
