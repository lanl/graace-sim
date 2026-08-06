"""Bookkeeping for a run: who made it, when, and what it is.

Where the run's files live is a separate concern, handled by ``WorkingEnvironment`` in
``environment.py``.
"""

from pydantic import Field

from models.base import StrictModel


class Metadata(StrictModel):
    """Author, date, and description of a run."""

    author: str = Field(min_length=1)
    date: str = Field(min_length=1)
    description: str = Field(min_length=1)
