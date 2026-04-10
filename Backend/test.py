from utils import predict_all_models

sample = {
    "Age": 55,
    "Gender": "F",
    "Souches": "Escherichia coli",
    "Diabetes": "Yes",
    "Hypertension": "No",
    "Hospital_before": "Yes",
    "Infection_Freq": 2
}

print(predict_all_models(sample))