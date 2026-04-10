from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings

import yaml

BASE_DIR = Path(__file__).resolve().parent


class _DatabaseSettings(BaseSettings):
    user: str
    password: SecretStr
    host: str
    port: int
    name: str

    def get_database_url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"


class _Settings(BaseSettings):
    database: _DatabaseSettings

    @classmethod
    def load(cls) -> "_Settings":
        path = Path(BASE_DIR.parent, "config", "config.yaml")
        with open(path) as file:
            return cls(**yaml.safe_load(file))


settings = _Settings.load()
