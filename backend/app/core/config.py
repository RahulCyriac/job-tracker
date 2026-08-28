from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  model_config = SettingsConfigDict(
      env_file=".env", env_file_encoding="utf-8", extra="ignore"
  )

  PROJECT_NAME: str = "Job Application Tracker & Analytics Platform API"
  VERSION: str = "0.1.0"
  API_V1_STR: str = "/api/v1"
  
  POSTGRES_SERVER: str = "localhost"
  POSTGRES_PORT: int = 5436
  POSTGRES_USER: str = "postgres"
  POSTGRES_PASSWORD: str = "postgres"
  POSTGRES_DB: str = "job_tracker"
  DATABASE_URL_OVERRIDE: str | None = Field(
      default=None, validation_alias="DATABASE_URL"
  )

  @property
  def DATABASE_URL(self) -> str:
    if self.DATABASE_URL_OVERRIDE:
      url = self.DATABASE_URL_OVERRIDE
      if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
      elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
      return url
    return (
        f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
        f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    )

settings = Settings()