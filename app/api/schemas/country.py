"""Country schema definitions."""

from pydantic import BaseModel, Field, field_validator


class CountryCreateRequest(BaseModel):
    """Schema for country creation request"""

    name: str = Field(..., min_length=1, max_length=100, description="Country name")
    code: str = Field(
        ..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code"
    )

    @field_validator("code")
    @classmethod
    def validate_code_uppercase(cls, v: str) -> str:
        """Normalize country code to uppercase"""
        return v.upper()

    model_config = {
        "json_schema_extra": {"examples": [{"name": "Japan", "code": "JP"}]}
    }


class CountryUpdateRequest(BaseModel):
    """Schema for country update request"""

    name: str | None = Field(
        None, min_length=1, max_length=100, description="Country name"
    )
    code: str | None = Field(
        None, min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code"
    )

    @field_validator("code")
    @classmethod
    def validate_code_uppercase(cls, v: str | None) -> str | None:
        """Normalize country code to uppercase"""
        return v.upper() if v else None

    model_config = {
        "json_schema_extra": {"examples": [{"name": "United States", "code": "US"}]}
    }


class CountryResponse(BaseModel):
    """Schema for country response"""

    id: int = Field(..., description="Country ID")
    name: str = Field(..., description="Country name")
    code: str = Field(..., description="ISO 3166-1 alpha-2 country code")

    model_config = {
        "from_attributes": True,  # Enable conversion from SQLAlchemy models
        "json_schema_extra": {"examples": [{"id": 1, "name": "Japan", "code": "JP"}]},
    }


# Aliases for create/update responses (currently same as CountryResponse)
# These can be customized in the future if needed
CountryCreateResponse = CountryResponse
CountryUpdateResponse = CountryResponse
