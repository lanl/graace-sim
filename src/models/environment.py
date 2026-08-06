"""Where a run's files live: the working directory, the per-run directory, and
its log and results sub-directories.

These are computed paths only. Nothing here touches the filesystem — creating the
directories is the runner's job. The paths describe the layout:

    <working_directory>/<run_id>_<run_sub_number>/            the run directory
    <working_directory>/<run_id>_<run_sub_number>/logs/       summary and log files
    <working_directory>/<run_id>_<run_sub_number>/results/    gamma hit Parquet files
    <working_directory>/<run_id>_<run_sub_number>/<run_id>.mac the exact macro that ran
"""

from pathlib import Path

from pydantic import Field

from models.base import StrictModel


class WorkingEnvironment(StrictModel):
    """The run's working environment: Where the simulation outputs results and logs

    From the working directory and the run's identity, this derives the per-run
    directory, its ``logs/`` and ``results/`` sub-directories, and the path of
    the macro that ran. The values are computed paths only; 
    """

    working_directory: Path = Field(default=Path("data"))
    run_id: str = Field(default="example", min_length=1)
    sub_run: int = Field(default=0, ge=0, le=9999)

    @property
    def run_directory(self) -> Path:
        """The per-run directory: ``<working_directory>/<run_id>_<run_sub_number>``."""
        return self.working_directory / f"{self.run_id}_{self.sub_run:03d}"

    @property
    def log_directory(self) -> Path:
        """Where summary and log files are written."""
        return self.run_directory / "logs"

    @property
    def results_directory(self) -> Path:
        """Where the gamma hit Parquet files are written."""
        return self.run_directory / "results"

    @property
    def macro_file(self) -> Path:
        """The exact macro that ran for this run: ``<run_id>.mac``."""
        return self.run_directory / f"{self.run_id}.mac"
