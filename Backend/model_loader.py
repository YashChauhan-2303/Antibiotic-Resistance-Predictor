import os
import joblib
import gdown
from pathlib import Path
from logger_config import logger
from exceptions import ModelNotLoadedException
from config import settings


class ModelLoader:
    """Singleton class to load and cache models"""

    _instance = None
    _models = None
    _loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    def load_models(self, model_path: str = None):
        if model_path is None:
            model_path = settings.MODEL_PATH

        if self._loaded and self._models is not None:
            logger.debug("Models already loaded, returning cached version")
            return self._models

        try:
            full_path = Path(model_path)

            # 🔥 STEP 1: If file NOT present → download (Render case)
            if not full_path.exists():
                logger.warning(f"Model not found locally. Downloading from Google Drive...")

                url = "https://drive.google.com/uc?id=1fEvb3FJdrrraohY_rR16mHLWRi796Yi6"

                gdown.download(url, str(full_path), quiet=False)

                if not full_path.exists():
                    raise ModelNotLoadedException("Failed to download model file")

            # 🔥 STEP 2: Load model (works for both local + Render)
            logger.info(f"Loading models from {model_path}...")
            model_data = joblib.load(full_path)

            # Validate keys
            required_keys = ["preprocessor", "lr", "rf", "svm", "xgb_estimators", "bag", "ada"]
            missing_keys = [key for key in required_keys if key not in model_data]

            if missing_keys:
                error_msg = f"Missing keys in model file: {missing_keys}"
                logger.error(error_msg)
                raise ModelNotLoadedException(error_msg)

            self._models = model_data
            self._loaded = True

            logger.info("✓ Models loaded successfully!")
            return self._models

        except Exception as e:
            logger.error(f"✗ Error loading models: {str(e)}", exc_info=True)
            raise ModelNotLoadedException(str(e))

    def is_loaded(self):
        return self._loaded and self._models is not None

    def get_models(self):
        if not self.is_loaded():
            raise ModelNotLoadedException("Models not loaded. Call load_models() first.")
        return self._models


model_loader = ModelLoader()