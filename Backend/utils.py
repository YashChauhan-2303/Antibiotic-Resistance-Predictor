import pandas as pd
import numpy as np
import shap
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

CATEGORICAL_FEATURES = ["Gender", "Souches", "Diabetes", "Hypertension", "Hospital_before", "Age_Group"]

def get_clean_feature_names(pipeline):
    """Extracts beautifully formatted clinical labels from the fitted preprocessor."""
    preprocessor = pipeline.named_steps["preprocessor"]
    raw_names = preprocessor.get_feature_names_out()
    clean_names = []
    
    for name in raw_names:
        name = name.replace("num__", "").replace("bin__", "")
        if name.startswith("cat__"):
            part = name.replace("cat__", "")
            for cat_feat in CATEGORICAL_FEATURES:
                if part.startswith(cat_feat + "_"):
                    val = part[len(cat_feat)+1:]
                    clean_names.append(f"{cat_feat}: {val}")
                    break
            else:
                clean_names.append(part.replace("_", " "))
        else:
            clean_names.append(name.replace("_", " "))
            
    return clean_names

def engineer_features(patient_dict: dict, strain_freq_map: dict) -> dict:
    """Engineer the 7 clinical risk features from 7 raw clinical fields."""
    feats = patient_dict.copy()
    
    # 1. Age_Group
    age = feats.get("Age", 0)
    if age <= 18:
        feats["Age_Group"] = "Child"
    elif age <= 40:
        feats["Age_Group"] = "Young_Adult"
    elif age <= 60:
        feats["Age_Group"] = "Adult"
    else:
        feats["Age_Group"] = "Senior"
        
    # 2. Comorbidity_Score
    feats["Comorbidity_Score"] = (
        (1 if feats.get("Diabetes") == "Yes" else 0)
        +
        (1 if feats.get("Hypertension") == "Yes" else 0)
    )
    
    # 3. Hospital_Risk
    feats["Hospital_Risk"] = 1 if feats.get("Hospital_before") == "Yes" else 0
    
    # 4. Frequent_Infection
    feats["Frequent_Infection"] = 1 if feats.get("Infection_Freq", 0) >= 3 else 0
    
    # 5. High_Risk_Patient
    feats["High_Risk_Patient"] = 1 if (feats.get("Hospital_before") == "Yes" and feats.get("Infection_Freq", 0) >= 3) else 0
    
    # 6. Strain_Frequency
    strain = feats.get("Souches", "")
    feats["Strain_Frequency"] = strain_freq_map.get(strain, 0)
    
    # 7. Risk_Score
    feats["Risk_Score"] = (
        (1 if feats.get("Diabetes") == "Yes" else 0)
        +
        (1 if feats.get("Hypertension") == "Yes" else 0)
        +
        (1 if feats.get("Hospital_before") == "Yes" else 0)
        +
        (1 if feats.get("Infection_Freq", 0) >= 3 else 0)
    )
    
    return feats

def predict_xgboost(new_patient: dict, explain: bool = False):
    """Make predictions using per-antibiotic pipelines with optional SHAP explainability"""
    try:
        logger.info(f"Making predictions for patient: Age={new_patient.get('Age')}, Gender={new_patient.get('Gender')}, Explain={explain}")

        # Get model data
        model_data = model_loader.get_models()
        pipelines = model_data["pipelines"]
        thresholds = model_data["thresholds"]
        tiers = model_data["tiers"]
        strain_freq = model_data["strain_frequencies"]

        # 1. Feature Engineering
        engineered_patient = engineer_features(new_patient, strain_freq)
        
        # Enforce exact clinical feature column order
        features_ordered = [
            "Age", "Gender", "Souches", "Diabetes", "Hypertension", "Hospital_before", "Infection_Freq",
            "Age_Group", "Comorbidity_Score", "Hospital_Risk", "Frequent_Infection", "High_Risk_Patient",
            "Strain_Frequency", "Risk_Score"
        ]
        sample = pd.DataFrame([engineered_patient])[features_ordered]

        # Add Debug Logging
        print("Prediction DataFrame:")
        print(sample)
        print("\nColumn Types:")
        print(sample.dtypes)

        # Verify Training Compatibility
        expected_columns = [
            "Age", "Gender", "Souches", "Diabetes", "Hypertension", "Hospital_before", "Infection_Freq",
            "Age_Group", "Comorbidity_Score", "Hospital_Risk", "Frequent_Infection", "High_Risk_Patient",
            "Strain_Frequency", "Risk_Score"
        ]
        columns_match = list(sample.columns) == expected_columns
        print(f"\nTraining Compatibility Verified: {columns_match}\n")

        result = []
        for antibiotic in ANTIBIOTIC_COLS:
            if antibiotic not in pipelines:
                logger.warning(f"No pipeline loaded for antibiotic '{antibiotic}'. Skipping.")
                continue

            pipeline = pipelines[antibiotic]
            threshold = thresholds[antibiotic]
            tier = tiers[antibiotic]

            # Get raw probability of resistance (class 1)
            prob_resistant = float(pipeline.predict_proba(sample)[0][1])
            prediction_label = "Resistant" if prob_resistant >= threshold else "Susceptible"

            # Confidence Tier Classification System
            if prob_resistant > 0.80 or prob_resistant < 0.20:
                confidence = "High"
            elif (0.60 <= prob_resistant <= 0.80) or (0.20 <= prob_resistant <= 0.40):
                confidence = "Medium"
            else:
                confidence = "Low"

            # Model Tier (Capitalized)
            model_tier_cap = "Production" if tier.lower() == "production" else "Experimental"

            # Compute local SHAP explanation if requested
            explanation_data = None
            if explain:
                try:
                    preprocessor = pipeline.named_steps["preprocessor"]
                    classifier = pipeline.named_steps["classifier"]
                    
                    # Preprocess raw sample
                    X_trans = preprocessor.transform(sample)
                    if hasattr(X_trans, "toarray"):
                        X_trans = X_trans.toarray()

                    # SHAP Tree Explainer
                    explainer = shap.TreeExplainer(classifier)
                    shap_values = explainer.shap_values(X_trans)[0]
                    clean_feats = get_clean_feature_names(pipeline)

                    factors = []
                    for name, val in zip(clean_feats, shap_values):
                        if abs(val) > 0.001:
                            factors.append({
                                "feature": name,
                                "direction": "positive" if val > 0 else "negative",
                                "impact": round(float(val), 4)
                            })
                    
                    # Sort by magnitude of contribution
                    factors = sorted(factors, key=lambda x: abs(x["impact"]), reverse=True)

                    explanation_data = {
                        "top_positive_factors": [f["feature"] for f in factors if f["direction"] == "positive"][:3],
                        "top_negative_factors": [f["feature"] for f in factors if f["direction"] == "negative"][:3]
                    }
                except Exception as shap_err:
                    logger.error(f"Failed to generate SHAP explanation for '{antibiotic}': {shap_err}")
                    explanation_data = {
                        "top_positive_factors": [],
                        "top_negative_factors": []
                    }

            row = {
                "antibiotic": antibiotic,
                "prediction": prediction_label,
                "probability": round(prob_resistant, 2),
                "confidence": confidence,
                "model_tier": model_tier_cap,
                "decision_threshold": round(threshold, 2),
                "explanation": explanation_data
            }
            result.append(row)

        logger.info(f"SUCCESS: Prediction completed successfully for {len(result)} antibiotics")
        return result

    except Exception as e:
        error_msg = f"Prediction error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise PredictionException(error_msg)
