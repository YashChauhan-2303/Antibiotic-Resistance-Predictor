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


def get_consensus_prediction(predictions: dict, antibiotic_idx: int):
    votes = []

    for model_name, preds in predictions.items():
        value = preds[antibiotic_idx]

        # Fix nested/array values
        if isinstance(value, np.ndarray):
            value = value.item()

        votes.append(int(value))

    resistant_count = sum(votes)
    susceptible_count = len(votes) - resistant_count

    if resistant_count == susceptible_count:
        consensus = "Uncertain"
    else:
        consensus = "Resistant" if resistant_count > susceptible_count else "Susceptible"

    confidence = abs(resistant_count - susceptible_count) / len(votes)

    return {
        "consensus": consensus,
        "confidence": round(confidence * 100, 1),
        "resistant_votes": resistant_count,
        "susceptible_votes": susceptible_count,
    }


def predict_all_models(new_patient: dict):
    """Make predictions using all loaded models"""
    try:
        logger.info(f"Making prediction for patient: Age={new_patient.get('Age')}, Gender={new_patient.get('Gender')}")

        # Get models
        models = model_loader.get_models()
        preprocessor = models["preprocessor"]
        lr_model = models["lr"]
        rf_model = models["rf"]
        svm_model = models["svm"]
        xgb_estimators = models["xgb_estimators"]
        bag_model = models["bag"]
        ada_model = models["ada"]

        # Preprocess input
        sample = pd.DataFrame([new_patient])
        X_pp = preprocessor.transform(sample)

        # Get predictions from all models
        model_preds = {
            "Logistic Regression": lr_model.predict(X_pp)[0],
            "Random Forest": rf_model.predict(X_pp)[0],
            "SVM": svm_model.predict(X_pp)[0],
            "XGBoost": np.array([est.predict(X_pp)[0] for est in xgb_estimators]),
            "Bagging": bag_model.predict(X_pp)[0],
            "AdaBoost": ada_model.predict(X_pp)[0],
        }

        # Format results
        result = []
        for ab in ANTIBIOTIC_COLS:
            idx = ANTIBIOTIC_COLS.index(ab)
            row = {"antibiotic": ab}

            # Individual model predictions
            for model_name, preds in model_preds.items():
                row[model_name] = "Resistant" if preds[idx] == 1 else "Susceptible"

            # Consensus prediction
            consensus = get_consensus_prediction(model_preds, idx)
            row["consensus"] = consensus["consensus"]
            row["confidence"] = consensus["confidence"]
            row["resistant_votes"] = consensus["resistant_votes"]
            row["susceptible_votes"] = consensus["susceptible_votes"]

            result.append(row)

        logger.info(f"✓ Prediction completed successfully for {len(result)} antibiotics")
        return result

    except Exception as e:
        error_msg = f"Prediction error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise PredictionException(error_msg)
    
