import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    STORAGE_DIR: str = os.getenv('STORAGE_DIR', './data')

settings = Settings()