import re

from pydantic import BaseModel, Field, field_validator


class StateCreate(BaseModel):
    """Schema for creating a state/province"""

    country_id: int = Field(..., description="Country ID")
    name: str = Field(..., min_length=1, max_length=100, description="State/province name")
    code: str = Field(
        ..., min_length=1, max_length=10, description="ISO 3166-2 format code"
    )

    @field_validator("code")
    @classmethod
    def validate_code_format(cls, v: str) -> str:
        """
        Normalize code to uppercase and validate ISO 3166-2 format

        ISO 3166-2 format: {country code}-{subdivision code}
        Examples: JP-13 (Tokyo), US-CA (California)
        """
        v = v.upper()
        # Check basic ISO 3166-2 pattern
        if not re.match(r"^[A-Z]{2}-[A-Z0-9]{1,3}$", v):
            raise ValueError(
                "code must be in ISO 3166-2 format (e.g., 'JP-13', 'US-CA')"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{"country_id": 1, "name": "Tokyo", "code": "JP-13"}]
        }
    }


class StateCreateNested(BaseModel):
    """Schema for creating a state/province (nested endpoint)"""

    name: str = Field(..., min_length=1, max_length=100, description="State/province name")
    code: str = Field(
        ..., min_length=1, max_length=10, description="ISO 3166-2 format code"
    )

    @field_validator("code")
    @classmethod
    def validate_code_format(cls, v: str) -> str:
        """
        Normalize code to uppercase and validate ISO 3166-2 format

        ISO 3166-2 format: {country code}-{subdivision code}
        Examples: JP-13 (Tokyo), US-CA (California)
        """
        v = v.upper()
        # Check basic ISO 3166-2 pattern
        if not re.match(r"^[A-Z]{2}-[A-Z0-9]{1,3}$", v):
            raise ValueError(
                "code must be in ISO 3166-2 format (e.g., 'JP-13', 'US-CA')"
            )
        return v

    model_config = {
        "json_schema_extra": {"examples": [{"name": "Tokyo", "code": "JP-13"}]}
    }


class StateUpdate(BaseModel):
    """Schema for updating a state/province"""

    country_id: int | None = Field(None, description="Country ID")
    name: str | None = Field(
        None, min_length=1, max_length=100, description="State/province name"
    )
    code: str | None = Field(
        None, min_length=1, max_length=10, description="ISO 3166-2 format code"
    )

    @field_validator("code")
    @classmethod
    def validate_code_format(cls, v: str | None) -> str | None:
        """
        Normalize code to uppercase and validate ISO 3166-2 format

        ISO 3166-2 format: {country code}-{subdivision code}
        Examples: JP-13 (Tokyo), US-CA (California)
        """
        if v is None:
            return None
        v = v.upper()
        # Check basic ISO 3166-2 pattern
        if not re.match(r"^[A-Z]{2}-[A-Z0-9]{1,3}$", v):
            raise ValueError(
                "code must be in ISO 3166-2 format (e.g., 'JP-13', 'US-CA')"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{"name": "California", "code": "US-CA"}]
        }
    }


class StateResponse(BaseModel):
    """Schema for state/province response"""

    id: int = Field(..., description="State/province ID")
    country_id: int = Field(..., description="Country ID")
    name: str = Field(..., description="State/province name")
    code: str = Field(..., description="ISO 3166-2 format code")

    model_config = {
        "from_attributes": True,  # Enable conversion from SQLAlchemy models
        "json_schema_extra": {
            "examples": [{"id": 1, "country_id": 1, "name": "Tokyo", "code": "JP-13"}]
        },
    }
