from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    app_name: str = "CyberPath AI"
    debug: bool = False
    database_url: str = os.getenv("DATABASE_URL", "")
    mistral_api_key: str = ""
    secret_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
