from pydantic_settings import BaseSettings
import os


class DevelopmentConfig(BaseSettings):
    debug: bool = True
    database_url: str = os.getenv("DATABASE_URL", "")
    reload: bool = True


class ProductionConfig(BaseSettings):
    debug: bool = False
    database_url: str = os.getenv("DATABASE_URL", "")
    reload: bool = False


class TestingConfig(BaseSettings):
    debug: bool = True
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    reload: bool = False
