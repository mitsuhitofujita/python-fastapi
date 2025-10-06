from pydantic import BaseModel, Field, field_validator


class CountryCreate(BaseModel):
    """国作成用スキーマ"""

    name: str = Field(..., min_length=1, max_length=100, description="国名")
    code: str = Field(
        ..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 国コード"
    )

    @field_validator("code")
    @classmethod
    def validate_code_uppercase(cls, v: str) -> str:
        """国コードを大文字に統一"""
        return v.upper()

    model_config = {
        "json_schema_extra": {"examples": [{"name": "Japan", "code": "JP"}]}
    }


class CountryUpdate(BaseModel):
    """国更新用スキーマ"""

    name: str | None = Field(None, min_length=1, max_length=100, description="国名")
    code: str | None = Field(
        None, min_length=2, max_length=2, description="ISO 3166-1 alpha-2 国コード"
    )

    @field_validator("code")
    @classmethod
    def validate_code_uppercase(cls, v: str | None) -> str | None:
        """国コードを大文字に統一"""
        return v.upper() if v else None

    model_config = {
        "json_schema_extra": {"examples": [{"name": "United States", "code": "US"}]}
    }


class CountryResponse(BaseModel):
    """国応答用スキーマ"""

    id: int = Field(..., description="国ID")
    name: str = Field(..., description="国名")
    code: str = Field(..., description="ISO 3166-1 alpha-2 国コード")

    model_config = {
        "from_attributes": True,  # SQLAlchemy モデルから変換可能にする
        "json_schema_extra": {"examples": [{"id": 1, "name": "Japan", "code": "JP"}]},
    }
