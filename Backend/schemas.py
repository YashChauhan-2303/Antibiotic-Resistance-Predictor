from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any


class PatientInput(BaseModel):
    """Schema for patient input data - validated input"""

    Age: float = Field(..., ge=0, le=150, description="Patient age in years (0-150)")
    Gender: str = Field(..., description="Patient gender (M or F)")
    Souches: str = Field(..., min_length=1, description="Bacterial strain/species")
    Diabetes: str = Field(..., description="Diabetes status (Yes or No)")
    Hypertension: str = Field(..., description="Hypertension status (Yes or No)")
    Hospital_before: str = Field(..., description="Previous hospitalization (Yes or No)")
    Infection_Freq: float = Field(..., ge=0, description="Infection frequency (≥ 0)")

    @field_validator("Gender")
    @classmethod
    def validate_gender(cls, v):
        if v.upper() not in ["M", "F"]:
            raise ValueError("Gender must be 'M' or 'F'")
        return v.upper()

    @field_validator("Diabetes", "Hypertension", "Hospital_before")
    @classmethod
    def validate_yes_no(cls, v):
        if v not in ["Yes", "No"]:
            raise ValueError("Value must be 'Yes' or 'No'")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "Age": 55,
                "Gender": "F",
                "Souches": "Escherichia coli",
                "Diabetes": "Yes",
                "Hypertension": "No",
                "Hospital_before": "Yes",
                "Infection_Freq": 2,
            }
        }


class AntibioticPrediction(BaseModel):
    """Schema for single antibiotic prediction"""

    antibiotic: str
    Logistic_Regression: str = Field(alias="Logistic Regression")
    Random_Forest: str = Field(alias="Random Forest")
    SVM: str
    XGBoost: str
    Bagging: str
    AdaBoost: str
    consensus: str = Field(..., description="Consensus prediction from all models")
    confidence: float = Field(..., ge=0, le=100, description="Confidence percentage (0-100)")
    resistant_votes: int = Field(..., ge=0, le=6, description="Number of models predicting Resistant")
    susceptible_votes: int = Field(..., ge=0, le=6, description="Number of models predicting Susceptible")

    class Config:
        populate_by_name = True


class PredictionSummary(BaseModel):
    """Summary statistics of predictions"""

    total_antibiotics: int
    resistant_count: int
    susceptible_count: int
    resistant_percentage: float
    susceptible_percentage: float
    high_confidence_resistant: List[str] = Field(..., description="Antibiotics with >80% confidence resistant")
    high_confidence_susceptible: List[str] = Field(..., description="Antibiotics with >80% confidence susceptible")
    recommended_antibiotics: List[str] = Field(..., description="Recommended antibiotics (susceptible with high confidence)")


class PredictionResponse(BaseModel):
    """Schema for complete prediction response"""

    status: str = "success"
    data: List[AntibioticPrediction] = Field(..., description="Predictions for each antibiotic")
    summary: PredictionSummary
    timestamp: str = Field(..., description="ISO format timestamp of prediction")

    class Config:
        json_schema_extra = {
            "description": "Complete prediction response with data and summary"
        }


class HealthCheckResponse(BaseModel):
    """Schema for health check response"""

    status: str
    models_loaded: bool
    environment: str
    version: str
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for error responses"""

    status: str = "error"
    error: str = Field(..., description="Error message")
    detail: Optional[str] = None
    status_code: int = Field(..., description="HTTP status code")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "error": "Validation error",
                "detail": "Gender must be 'M' or 'F'",
                "status_code": 422,
            }
        }


class APIInfoResponse(BaseModel):
    """Schema for API info response"""

    api_name: str
    version: str
    environment: str
    models: List[str]
    antibiotics: List[str]
    input_fields: Dict[str, str]
    endpoints: Dict[str, str]
