from pydantic_settings import BaseSettings


class DevelopmentConfig(BaseSettings):
    debug: bool = True
    database_url: str = "postgresql://user:pass@localhost:5432/cyberpath"
    reload: bool = True


class ProductionConfig(BaseSettings):
    debug: bool = False
    database_url: str = ""
    reload: bool = False


class TestingConfig(BaseSettings):
    debug: bool = True
    database_url: str = "sqlite:///./test.db"
    reload: bool = False
