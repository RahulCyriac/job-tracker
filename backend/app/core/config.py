import os
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
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

  DATABASE_URL: str | None = None

  @property
  def SQLALCHEMY_DATABASE_URI(self) -> str:
    # Direct check on OS process environment (covers Render, Railway, Docker, Neon)
    env_url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("DATABASE_URI")
        or os.environ.get("NEON_DATABASE_URL")
        or self.DATABASE_URL
    )
    if env_url:
      url = str(env_url).strip().strip("'").strip('"')
      # Convert postgres:// or postgresql:// to postgresql+asyncpg://
      if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
      elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

      # Clean and sanitize query parameters for asyncpg compatibility
      try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        # asyncpg does not accept channel_binding or target_session_attrs
        for unsupported_key in ["channel_binding", "target_session_attrs", "sslmode", "options"]:
          query_params.pop(unsupported_key, None)
        # Ensure ssl=require for cloud PostgreSQL (Neon, Supabase, RDS)
        query_params["ssl"] = ["require"]
        clean_query = urlencode(query_params, doseq=True)
        return urlunparse(parsed._replace(query=clean_query))
      except Exception:
        return url

    return (
        f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
        f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    )

settings = Settings()