import os


class Config:
    """Application settings read from the environment."""

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY") or os.urandom(32)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
