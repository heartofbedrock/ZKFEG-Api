import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    STORAGE_DIR: str = os.getenv('STORAGE_DIR', './data')

settings = Settings()