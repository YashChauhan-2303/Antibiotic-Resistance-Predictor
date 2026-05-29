import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings from environment variables"""

    # API
    API_TITLE = "Antibiotic Resistance Prediction API"
    API_VERSION = "1.0.0"
    API_PREFIX = "/api/v1"

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"

    # CORS
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")
    ALLOWED_ORIGINS = [
        FRONTEND_URL,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Model
    MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(os.path.dirname(__file__), "model_small.joblib"))
    MODELS_ROOT = os.getenv("MODELS_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models")))


    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

    # Security
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["*"]
    CORS_ALLOW_HEADERS = ["*"]

    @classmethod
    def get_log_level(cls):
        """Get log level from string"""
        levels = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50,
        }
        return levels.get(cls.LOG_LEVEL, 20)


settings = Settings()
