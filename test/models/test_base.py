"""The strict base rejects unknown fields and re-validates on assignment."""

import pytest
from pydantic import ValidationError

from models.base import StrictModel


class Example(StrictModel):
    value: int


def test_unknown_field_is_rejected():
    with pytest.raises(ValidationError):
        Example(value=1, unexpected=2)


def test_assignment_is_revalidated():
    example = Example(value=1)
    with pytest.raises(ValidationError):
        example.value = "not an int"
