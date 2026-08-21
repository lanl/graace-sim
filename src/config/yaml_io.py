"""Read a simulation configuration from YAML and validate it as a ``Simulation``."""

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
