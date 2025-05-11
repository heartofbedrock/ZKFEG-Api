import os

class Settings:
    # Where all session data lives
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./zk_sessions")

settings = Settings()
