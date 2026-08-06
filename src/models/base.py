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
