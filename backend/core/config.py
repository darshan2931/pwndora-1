from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CyberPath AI"
    debug: bool = False
    database_url: str = "postgresql://user:pass@localhost:5432/cyberpath"
    mistral_api_key: str = ""
    secret_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
