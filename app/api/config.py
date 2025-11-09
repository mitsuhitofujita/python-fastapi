from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Unknown environment variables are ignored
    )

    # Database settings
    database_url: str = "postgresql://postgres:postgres@postgres:5432/app_local"
    database_url_test: str = "postgresql://app_test:app_test@postgres:5432/app_test"

    # Logging settings
    log_level: str = "INFO"

    # SQLAlchemy settings
    sqlalchemy_echo: bool = (
        False  # SQL logging (True for development, False for production)
    )


# Global settings instance
settings = Settings()
