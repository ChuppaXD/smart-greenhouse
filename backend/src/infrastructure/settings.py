from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://greenhouse:greenhouse@localhost:5432/greenhouse"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file="../.env",  # Looks up one level to find your root .env file
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
