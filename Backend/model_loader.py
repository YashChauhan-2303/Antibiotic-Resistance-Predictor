import os
import json
import joblib
import pandas as pd
from pathlib import Path
from logger_config import logger
from exceptions import ModelNotLoadedException
from config import settings

class ModelLoader:
    """Singleton class to load and cache multiple per-antibiotic pipelines and thresholds"""

    _instance = None
    _models = None
    _loaded = False

    # Default fallback strain frequencies calculated from cleaned_output_v2.csv
    FALLBACK_STRAIN_FREQUENCIES = {
        'Escherichia coli': 6083,
        'Enterobacteria spp.': 997,
        'Klebsiella pneumoniae': 702,
        'Proteus mirabilis': 598,
        'Citrobacter spp.': 481,
        'Morganella morganii': 305,
        'Serratia marcescens': 256,
        'Pseudomonas aeruginosa': 200,
        'Acinetobacter baumannii': 181,
        'Protus mirabilis': 51,
        'Proeus mirabilis': 47,
        'Prot.eus mirabilis': 46,
        'Unknown': 10
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    def load_models(self, models_root: str = None):
        """Load multiple pipelines and thresholds from models/production and models/experimental"""
        if models_root is None:
            models_root = settings.MODELS_ROOT

        if self._loaded and self._models is not None:
            logger.debug("Models already loaded, returning cached versions")
            return self._models

        try:
            root_path = Path(models_root)
            if not root_path.exists():
                error_msg = f"Models root directory not found: {root_path}"
                logger.error(error_msg)
                raise ModelNotLoadedException(error_msg)

            logger.info(f"Loading clinical decision support models from {root_path}...")

            pipelines = {}
            thresholds = {}
            tiers = {}

            # Load models and thresholds from both production and experimental directories
            for tier in ["production", "experimental"]:
                tier_dir = root_path / tier
                if not tier_dir.exists():
                    logger.warning(f"Tier directory {tier_dir} does not exist. Skipping.")
                    continue

                thresholds_file = tier_dir / "thresholds.json"
                if not thresholds_file.exists():
                    logger.warning(f"Thresholds file not found at {thresholds_file}. Skipping.")
                    continue

                with open(thresholds_file, "r") as f:
                    tier_thresholds = json.load(f)

                for ab_name, thresh in tier_thresholds.items():
                    thresholds[ab_name] = thresh
                    tiers[ab_name] = tier

                    # Sanitize antibiotic name to match filename pattern (replace / and space with _)
                    sanitized_name = ab_name.replace("/", "_").replace(" ", "_")
                    model_file = tier_dir / f"{sanitized_name}.joblib"

                    if not model_file.exists():
                        # If experimental has Acide nalidixique as Acide_nalidixique, check if it's there
                        logger.error(f"Pipeline model file not found for '{ab_name}' at: {model_file}")
                        raise ModelNotLoadedException(f"Pipeline file not found for '{ab_name}'")

                    logger.info(f"  - Loading {tier} pipeline for {ab_name}...")
                    pipeline = joblib.load(model_file)
                    pipelines[ab_name] = pipeline

            # Calculate strain frequencies from v2 dataset for clinical feature engineering
            strain_frequencies = self.FALLBACK_STRAIN_FREQUENCIES
            data_file = root_path.parent / "data" / "cleaned_output_v2.csv"
            if data_file.exists():
                try:
                    logger.info(f"Computing strain frequencies from active production dataset: {data_file}")
                    df_data = pd.read_csv(data_file)
                    if "Souches" in df_data.columns:
                        strain_frequencies = df_data["Souches"].value_counts().to_dict()
                        logger.info("SUCCESS: Dynamically loaded strain frequencies from CSV")
                except Exception as ex:
                    logger.warning(f"Failed to read dataset to compute strain frequencies: {ex}. Using pre-compiled fallback.")
            else:
                logger.warning(f"Production dataset not found at {data_file}. Using pre-compiled fallback strain frequencies.")

            self._models = {
                "pipelines": pipelines,
                "thresholds": thresholds,
                "tiers": tiers,
                "strain_frequencies": strain_frequencies
            }
            self._loaded = True
            logger.info(f"SUCCESS: Successfully loaded {len(pipelines)} per-antibiotic XGBoost pipelines.")
            logger.info(f"  - Production models: {sum(1 for t in tiers.values() if t == 'production')}")
            logger.info(f"  - Experimental models: {sum(1 for t in tiers.values() if t == 'experimental')}")
            return self._models

        except Exception as e:
            logger.error(f"ERROR: Error loading pipelines: {str(e)}", exc_info=True)
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
