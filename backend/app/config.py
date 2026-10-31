from pathlib import Path
from typing import Annotated

from pydantic import HttpUrl, PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# Resolve .env relative to backend/ so it loads regardless of the working directory.
# In deployed environments there is no .env file; real env vars take precedence.
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    supabase_url: HttpUrl
    supabase_anon_key: SecretStr
    supabase_service_role_key: SecretStr

    database_url: PostgresDsn

    openai_api_key: SecretStr
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = 1536

    # NoDecode: the env var is comma-separated, not JSON.
    allowed_origins: Annotated[list[str], NoDecode] = []

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


# Instantiated at import so missing or invalid config fails at startup.
settings = Settings()
