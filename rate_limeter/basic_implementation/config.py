from pydantic_settings import BaseSettings
from typing import Optional 

class Settings(BaseSettings):
    # Radis configuration
    redis_host: str = "localhost"
    redis_port:int = 6379
    redis_db:int = 0
    resids_password: Optional[str] = None

    # Rate limiter configuration
    default_capacity:int = 10
    default_refile_rate:int = 5
    default_window_seconds:int = 60 

    # Application configuration
    app_title:str = "Basic Rate Limiter API"
    app_version:str = "1.0.0" 
    debug:bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True 

settings = Settings()
"""Global settings instance for the application."""
