import logging
import logging.handlers
import os
from config import settings

# Create logs directory
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

def setup_logging():
    """Configure logging for the application"""

    logger = logging.getLogger("antibiotic_api")
    logger.setLevel(settings.get_log_level())

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.get_log_level())

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    file_handler.setLevel(settings.get_log_level())

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()
