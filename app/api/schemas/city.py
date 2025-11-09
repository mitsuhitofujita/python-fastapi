"""City schema definitions."""

import re

from pydantic import BaseModel, Field, field_validator


class CityCreateRequest(BaseModel):
    """Schema for city/municipality creation request"""

    state_id: int = Field(..., gt=0, description="State ID that this city belongs to")
    name: str = Field(..., min_length=1, max_length=100, description="City name")
    code: str = Field(
        ..., description="City code (6-digit local government code, JIS X 0402)"
    )
    is_active: bool = Field(
        default=True, description="Whether the city is currently active"
    )

    @field_validator("code")
    @classmethod
    def validate_code_format(cls, v: str) -> str:
        """
        Validate city code format (6-digit number)

        City code follows JIS X 0402 standard (全国地方公共団体コード)
        Examples: 131016 (Minato-ku, Tokyo), 141003 (Tsurumi-ku, Yokohama)
        """
        if not re.match(r"^[0-9]{6}$", v):
            raise ValueError(
                "Code must be a 6-digit number (e.g., '131016' for Minato-ku, Tokyo)"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"state_id": 1, "name": "港区", "code": "131016", "is_active": True}
            ]
        }
    }


class CityUpdateRequest(BaseModel):
    """Schema for city/municipality update request"""

    name: str | None = Field(
        default=None, min_length=1, max_length=100, description="City name"
    )
    code: str | None = Field(
        default=None, description="City code (6-digit local government code)"
    )
    is_active: bool | None = Field(
        default=None, description="Whether the city is currently active"
    )

    @field_validator("code")
    @classmethod
    def validate_code_format(cls, v: str | None) -> str | None:
        """
        Validate city code format (6-digit number)

        City code follows JIS X 0402 standard (全国地方公共団体コード)
        Examples: 131016 (Minato-ku, Tokyo), 141003 (Tsurumi-ku, Yokohama)
        """
        if v is None:
            return None
        if not re.match(r"^[0-9]{6}$", v):
            raise ValueError(
                "Code must be a 6-digit number (e.g., '131016' for Minato-ku, Tokyo)"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{"name": "横浜市鶴見区", "code": "141003", "is_active": True}]
        }
    }


class CityResponse(BaseModel):
    """Schema for city/municipality response"""

    id: int = Field(..., description="City ID")
    state_id: int = Field(..., description="State ID")
    name: str = Field(..., description="City name")
    code: str = Field(..., description="City code (6-digit local government code)")
    is_active: bool = Field(..., description="Whether the city is currently active")

    model_config = {
        "from_attributes": True,  # Enable conversion from SQLAlchemy models
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "state_id": 1,
                    "name": "港区",
                    "code": "131016",
                    "is_active": True,
                }
            ]
        },
    }


# Aliases for create/update responses (currently same as CityResponse)
# These can be customized in the future if needed
CityCreateResponse = CityResponse
CityUpdateResponse = CityResponse
