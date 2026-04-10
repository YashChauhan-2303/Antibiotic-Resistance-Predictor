import joblib
from pathlib import Path
from logger_config import logger
from exceptions import ModelNotLoadedException
from config import settings


class ModelLoader:
    """Singleton class to load and cache models from joblib file"""

    _instance = None
    _models = None
    _loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    def load_models(self, model_path: str = None):
        """Load models from joblib file"""
        if model_path is None:
            model_path = settings.MODEL_PATH

        if self._loaded and self._models is not None:
            logger.debug("Models already loaded, returning cached version")
            return self._models

        try:
            # Check if file exists
            full_path = Path(model_path)
            if not full_path.exists():
                error_msg = f"Model file not found: {full_path}"
                logger.error(error_msg)
                raise ModelNotLoadedException(error_msg)

            logger.info(f"Loading models from {model_path}...")
            model_data = joblib.load(model_path)

            # Validate required keys
            required_keys = ["preprocessor", "lr", "rf", "svm", "xgb_estimators", "bag", "ada"]
            missing_keys = [key for key in required_keys if key not in model_data]

            if missing_keys:
                error_msg = f"Missing keys in model file: {missing_keys}"
                logger.error(error_msg)
                raise ModelNotLoadedException(error_msg)

            self._models = model_data
            self._loaded = True
            logger.info(f"✓ Successfully loaded models from {model_path}")
            logger.info(f"  - Models available: {list(model_data.keys())}")
            return self._models

        except Exception as e:
            logger.error(f"✗ Error loading models: {str(e)}", exc_info=True)
            raise ModelNotLoadedException(str(e))

    def is_loaded(self):
        """Check if models are loaded"""
        return self._loaded and self._models is not None

    def get_models(self):
        """Get cached models"""
        if not self.is_loaded():
            raise ModelNotLoadedException("Models not loaded. Call load_models() first.")
        return self._models

    @classmethod
    def reset(cls):
        """Reset the singleton (useful for testing)"""
        if cls._instance:
            cls._instance._models = None
            cls._instance._loaded = False


# Global instance
model_loader = ModelLoader()
