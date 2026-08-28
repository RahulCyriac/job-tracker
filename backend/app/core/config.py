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

  # Direct cloud database URL from environment variable:
  DATABASE_URL: str | None = None

  @property
  def SQLALCHEMY_DATABASE_URI(self) -> str:
    if self.DATABASE_URL:
      url = str(self.DATABASE_URL)
      # Convert postgres:// or postgresql:// to postgresql+asyncpg://
      if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
      elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
      # Fix sslmode parameter for asyncpg
      if "sslmode=require" in url:
        url = url.replace("sslmode=require", "ssl=require")
      return url
    return (
        f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
        f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    )

  # Backwards compatibility alias
  @property
  def DB_URL(self) -> str:
    return self.SQLALCHEMY_DATABASE_URI

settings = Settings()