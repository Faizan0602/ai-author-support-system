from functools import lru_cache

from pydantic import Field, HttpUrl
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """
    Centralized application settings.
    """

    APP_NAME: str = "AI Author Support System"

    # Gemini
    GEMINI_API_KEY: str = Field(
        ...,
        min_length=1,
        description="Google Gemini API Key",
    )

    # Supabase
    SUPABASE_URL: HttpUrl = Field(
        ...,
        description="Supabase Project URL",
    )

    SUPABASE_KEY: str = Field(
        ...,
        min_length=1,
        description="Supabase API Key",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Prefer backend/.env locally so stale OS variables do not win.
        """

        return (
            init_settings,
            dotenv_settings,
            env_settings,
            file_secret_settings,
        )


@lru_cache
def get_settings() -> Settings:
    """
    Returns cached application settings.
    """

    return Settings()
