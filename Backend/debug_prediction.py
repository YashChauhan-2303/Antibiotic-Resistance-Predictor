import os
import sys
import joblib
import pandas as pd
import numpy as np

# Define paths relative to this script
backend_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.abspath(os.path.join(backend_dir, "..", "models", "production", "AMX_AMP.joblib"))

print("=== Standalone Diagnostic Prediction Script ===")
print(f"Python Version: {sys.version}")
try:
    import sklearn
    print(f"scikit-learn Version: {sklearn.__version__}")
except ImportError:
    print("scikit-learn is not installed!")
try:
    print(f"pandas Version: {pd.__version__}")
except NameError:
    print("pandas is not installed!")
try:
    print(f"numpy Version: {np.__version__}")
except NameError:
    print("numpy is not installed!")

print("-" * 50)
print(f"Checking if model file exists: {model_path}")
if not os.path.exists(model_path):
    print(f"ERROR: Model file does not exist at {model_path}!")
    sys.exit(1)

def fix_imputer_compatibility(estimator):
    """Recursively search for SimpleImputer instances and patch missing or incorrect attributes like _fill_dtype due to scikit-learn version mismatch"""
    if estimator is None:
        return
        
    class_name = estimator.__class__.__name__
    if class_name == "SimpleImputer":
        try:
            # Detect if the imputer is for categorical features by checking statistics_
            is_categorical = False
            if hasattr(estimator, "statistics_") and estimator.statistics_ is not None:
                if any(isinstance(val, str) for val in estimator.statistics_):
                    is_categorical = True
            
            # Unconditionally force categorical imputer's _fill_dtype to object
            if is_categorical:
                estimator._fill_dtype = object
                print("SUCCESS: Forced categorical SimpleImputer _fill_dtype to object")
            else:
                import numpy as np
                estimator._fill_dtype = np.float64
                print("SUCCESS: Forced numerical SimpleImputer _fill_dtype to np.float64")
        except Exception as ex:
            try:
                estimator._fill_dtype = object
            except Exception:
                pass
            print(f"Failed to patch SimpleImputer: {ex}")

    elif "XGB" in class_name or "Classifier" in class_name or "Model" in class_name:
        try:
            # Self-healing parameter recovery loop
            while True:
                try:
                    if hasattr(estimator, "get_params"):
                        estimator.get_params(deep=False)
                    break
                except AttributeError as ae:
                    err_str = str(ae)
                    if "object has no attribute" in err_str:
                        attr_name = err_str.split("attribute")[-1].replace("'", "").strip()
                        setattr(estimator, attr_name, None)
                        print(f"SUCCESS: Self-healed missing constructor parameter: {attr_name} = None on {class_name}")
                    else:
                        raise
        except Exception as ex:
            print(f"Failed to self-heal: {ex}")

        # Also recursively patch all nested sub-objects in estimator's __dict__
        if hasattr(estimator, "__dict__"):
            for val in list(estimator.__dict__.values()):
                if hasattr(val, "__dict__"):
                    fix_imputer_compatibility(val)
                
    # Recursively traverse steps or transformers
    if hasattr(estimator, "steps"):  # Pipeline
        for name, step in estimator.steps:
            fix_imputer_compatibility(step)
            
    if hasattr(estimator, "transformers"):  # ColumnTransformer
        for name, trans, cols in estimator.transformers:
            fix_imputer_compatibility(trans)
            
    if hasattr(estimator, "transformers_"):  # ColumnTransformer fitted transformers_
        for name, trans, cols in estimator.transformers_:
            fix_imputer_compatibility(trans)
            
    if hasattr(estimator, "named_steps"):  # Pipeline named_steps
        for name, step in estimator.named_steps.items():
            fix_imputer_compatibility(step)

print("Loading pipeline...")
try:
    pipeline = joblib.load(model_path)
    fix_imputer_compatibility(pipeline)
    print("SUCCESS: Pipeline loaded and patched successfully!")
except Exception as e:
    print(f"FAILURE: Failed to load pipeline: {e}")
    sys.exit(1)

# Construct sample input matching expected schema
sample_dict = {
    "Age": 55.0,
    "Gender": "F",
    "Souches": "Escherichia coli",
    "Diabetes": "Yes",
    "Hypertension": "No",
    "Hospital_before": "Yes",
    "Infection_Freq": 2.0,
    "Age_Group": "Adult",
    "Comorbidity_Score": 1,
    "Hospital_Risk": 1,
    "Frequent_Infection": 0,
    "High_Risk_Patient": 0,
    "Strain_Frequency": 6083,
    "Risk_Score": 2
}

features_ordered = [
    "Age", "Gender", "Souches", "Diabetes", "Hypertension", "Hospital_before", "Infection_Freq",
    "Age_Group", "Comorbidity_Score", "Hospital_Risk", "Frequent_Infection", "High_Risk_Patient",
    "Strain_Frequency", "Risk_Score"
]

sample_df = pd.DataFrame([sample_dict])[features_ordered]

print("-" * 50)
print("Constructed Sample DataFrame:")
print(sample_df)
print("\nDataFrame Column Types:")
print(sample_df.dtypes)
print(f"Columns match expected training features exact list: {list(sample_df.columns) == features_ordered}")

print("-" * 50)
print("Executing pipeline.predict_proba(sample_df)...")
try:
    prob = pipeline.predict_proba(sample_df)
    print(f"SUCCESS! Raw Prediction Probabilities: {prob}")
except Exception as e:
    print("FAILURE! Prediction failed with the following traceback:")
    import traceback
    traceback.print_exc()
