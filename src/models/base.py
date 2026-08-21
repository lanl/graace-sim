"""The strict base model for the whole configuration schema."""

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Base model with strict validation defaults.

    Every model in the schema inherits from this so that unknown fields are
    rejected and assignments are re-validated.
    """

    model_config = ConfigDict(
        extra="forbid",            # reject unknown fields
        validate_assignment=True,  # re-validate when a field is changed
    )


def check_directory_safe_name(value: str, field: str) -> str:
    """Reject a name that would be unsafe used as a directory.

    The run id and each detector name both become directory names, so they must
    not contain a path separator or be the ``.``/``..`` directory entries.
    ``field`` names the field being checked so the error points at it.
    """
    if "/" in value or "\\" in value:
        raise ValueError(f"`{field}` must not contain a path separator.")
    if value in {".", ".."}:
        raise ValueError(f"`{field}` must not be '.' or '..'.")
    return value
