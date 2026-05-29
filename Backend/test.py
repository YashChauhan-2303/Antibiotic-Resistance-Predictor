from model_loader import model_loader
from utils import predict_xgboost
import json

# Pre-load the models
print("Loading models...")
model_loader.load_models()
print("Models loaded successfully!")

sample = {
    "Age": 55.0,
    "Gender": "F",
    "Souches": "Escherichia coli",
    "Diabetes": "Yes",
    "Hypertension": "No",
    "Hospital_before": "Yes",
    "Infection_Freq": 2.0
}

print("\n--- Predictions WITHOUT SHAP explanations ---")
res_no_explain = predict_xgboost(sample, explain=False)
# Show the first prediction as an example
print(json.dumps(res_no_explain[0], indent=2))

print("\n--- Predictions WITH SHAP explanations ---")
res_explain = predict_xgboost(sample, explain=True)
# Show the first prediction (production model e.g. AMX/AMP) as an example
print(json.dumps(res_explain[0], indent=2))