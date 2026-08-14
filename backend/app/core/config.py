from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  PROJECT_NAME: str = "Job Application Tracker & Analytics Platform API"
  VERSION: str = "0.1.0"
  API_V1_STR: str = "/api/v1"
  
  POSTGRES_SERVER: str = "localhost"
  POSTGRES_PORT: int = 5436
  POSTGRES_USER: str = "postgres"
  POSTGRES_PASSWORD: str = "postgres"
  POSTGRES_DB: str = "job_tracker"

  @property
  def DATABASE_URL(self) -> str:
    return (
        f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
        f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    )

settings = Settings()