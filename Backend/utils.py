import pandas as pd
import numpy as np
from logger_config import logger
from model_loader import model_loader
from exceptions import PredictionException

ANTIBIOTIC_COLS = [
    "AMX/AMP",
    "AMC",
    "CZ",
    "FOX",
    "CTX/CRO",
    "IPM",
    "GEN",
    "AN",
    "Acide nalidixique",
    "ofx",
    "CIP",
    "C",
    "Co-trimoxazole",
    "Furanes",
    "colistine",
]


def predict_xgboost(new_patient: dict):
    """Make predictions using single XGBoost multi-output model"""
    try:
        logger.info(f"Making prediction for patient: Age={new_patient.get('Age')}, Gender={new_patient.get('Gender')}")

        # Get model data
        model_data = model_loader.get_models()
        preprocessor = model_data["preprocessor"]
        xgb_model = model_data["model"]
        thresholds = model_data["thresholds"]

        # Preprocess input
        sample = pd.DataFrame([new_patient])
        X_pp = preprocessor.transform(sample)

        # Make predictions for each antibiotic using the multi-output model
        result = []
        for idx, antibiotic in enumerate(ANTIBIOTIC_COLS):
            # Get the estimator for this antibiotic
            estimator = xgb_model.estimators_[idx]
            
            # Get probability of positive class (resistant)
            proba = estimator.predict_proba(X_pp)
            prob_resistant = proba[0][1]  # Probability of class 1 (resistant)
            
            # Apply threshold to get binary prediction
            threshold = thresholds[idx]
            prediction = 1 if prob_resistant >= threshold else 0
            prediction_label = "Resistant" if prediction == 1 else "Susceptible"
            
            # Confidence is the probability value, scaled to percentage
            confidence = prob_resistant * 100 if prediction == 1 else (1 - prob_resistant) * 100

            row = {
                "antibiotic": antibiotic,
                "prediction": prediction_label,
                "confidence": round(confidence, 1)
            }
            result.append(row)

        logger.info(f"✓ Prediction completed successfully for {len(result)} antibiotics")
        return result

    except Exception as e:
        error_msg = f"Prediction error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise PredictionException(error_msg)
    
