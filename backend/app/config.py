from ast import List
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Aplicação
    app_name: str = "Gabarito Reader"
    app_version: str = "1.0.0"
    debug: bool = True

    # Banco de dados
    database_url: str = "sqlite:///./gabarito.db"

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Upload
    max_file_size_mb: int = 10
    upload_dir: str = "uploads/"

    # Gabarito (configurável sem mexer no código)
    alternativas: List[str] = ["A", "B", "C", "D", "E"]

    class Config:
        env_file = ".env"


# Instância única usada em todo o projeto
settings = Settings()