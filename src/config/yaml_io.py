"""Read and write simulation configuration as YAML.

For now this reads a YAML file and validates it as a ``Simulation``. Writing a
``Simulation`` back out to YAML will live here too (a later pull request).
"""

from pathlib import Path

import yaml
from loguru import logger

from models.simulation import Simulation


def load_simulation(path: str | Path) -> Simulation:
    """Load a YAML config file and return a validated ``Simulation``.

    Reads the file with ``yaml.safe_load`` and validates the result. A
    ``pydantic.ValidationError`` is allowed to propagate so its field-naming
    message reaches the caller.
    """
    path = Path(path)
    logger.info("Loading simulation config from {}", path)
    with path.open() as file:
        data = yaml.safe_load(file)
    return Simulation.model_validate(data)
