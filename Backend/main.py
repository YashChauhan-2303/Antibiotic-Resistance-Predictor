"""
Antibiotic Resistance Prediction API
FastAPI application for ML-based antibiotic resistance predictions
"""

import os
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from config import settings
from logger_config import logger
from model_loader import model_loader
from schemas import (
    PatientInput,
    PredictionResponse,
    ErrorResponse,
    HealthCheckResponse,
    APIInfoResponse,
    AntibioticPrediction,
    PredictionSummary,
)
from utils import predict_xgboost, ANTIBIOTIC_COLS
from exceptions import APIException, ModelNotLoadedException, ValidationException

# Create logs directory
os.makedirs("logs", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("=" * 60)
    logger.info("🚀 Starting Antibiotic Resistance Prediction API")
    logger.info(f"   Version: {settings.API_VERSION}")
    logger.info(f"   Environment: {settings.ENVIRONMENT}")
    logger.info("=" * 60)

    try:
        model_loader.load_models()
        logger.info("✓ API started successfully")
    except Exception as e:
        logger.error(f"✗ Failed to start API: {str(e)}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("=" * 60)
    logger.info("🛑 Shutting down Antibiotic Resistance Prediction API")
    logger.info("=" * 60)


# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description="Predict antibiotic resistance using ensemble ML models",
    version=settings.API_VERSION,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error": "Validation error",
            "detail": str(exc.errors()),
            "status_code": 422,
        },
    )


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """Handle custom API exceptions"""
    logger.error(f"API error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": exc.message,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "status_code": 500,
        },
    )


# Routes
@app.get("/", tags=["Health"], response_model=dict)
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Antibiotic Resistance Prediction API",
        "status": "running",
        "version": settings.API_VERSION,
    }


@app.get(f"{settings.API_PREFIX}/health", tags=["Health"], response_model=HealthCheckResponse)
async def health_check():
    """Extended health check with model status"""
    try:
        is_loaded = model_loader.is_loaded()

        return HealthCheckResponse(
            status="healthy" if is_loaded else "unhealthy",
            models_loaded=is_loaded,
            environment=settings.ENVIRONMENT,
            version=settings.API_VERSION,
            message="All systems operational" if is_loaded else "Models not loaded",
        )
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            models_loaded=False,
            environment=settings.ENVIRONMENT,
            version=settings.API_VERSION,
            message=str(e),
        )


@app.post(
    f"{settings.API_PREFIX}/predict",
    response_model=PredictionResponse,
    tags=["Predictions"],
    responses={
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def predict(patient: PatientInput, explain: bool = False):
    """
    Make antibiotic resistance predictions for a patient with optional explainability.

    This endpoint uses 15 independent per-antibiotic XGBoost pipelines to predict resistance.

    **Model:**
    - XGBoost (independent per-antibiotic pipelines)

    **Input:** Patient data with 7 fields
    **Output:** Predictions for 15 antibiotics with confidence scores, tiers, and SHAP explainability.
    """
    try:
        if not model_loader.is_loaded():
            logger.error("Model not loaded for prediction")
            raise ModelNotLoadedException("ML model not initialized. Server may still be starting.")

        logger.info(f"Processing prediction request for patient Age={patient.Age}, Gender={patient.Gender}, Explain={explain}")

        # Convert input to dictionary
        patient_dict = patient.model_dump()

        # Make predictions
        predictions = predict_xgboost(patient_dict, explain=explain)


        # Build summary
        resistant_antibiotics = [p["antibiotic"] for p in predictions if p["prediction"] == "Resistant"]
        susceptible_antibiotics = [p["antibiotic"] for p in predictions if p["prediction"] == "Susceptible"]

        high_confidence_resistant = [
            p["antibiotic"]
            for p in predictions
            if p["prediction"] == "Resistant" and p["confidence"] == "High"
        ]
        high_confidence_susceptible = [
            p["antibiotic"]
            for p in predictions
            if p["prediction"] == "Susceptible" and p["confidence"] == "High"
        ]

        # Recommended antibiotics: susceptible with high confidence
        recommended = high_confidence_susceptible[:5]  # Top 5

        summary = PredictionSummary(
            total_antibiotics=len(predictions),
            resistant_count=len(resistant_antibiotics),
            susceptible_count=len(susceptible_antibiotics),
            resistant_percentage=round((len(resistant_antibiotics) / len(predictions)) * 100, 1),
            susceptible_percentage=round((len(susceptible_antibiotics) / len(predictions)) * 100, 1),
            high_confidence_resistant=high_confidence_resistant,
            high_confidence_susceptible=high_confidence_susceptible,
            recommended_antibiotics=recommended,
        )

        logger.info(f"✓ Prediction completed: {len(predictions)} antibiotics analyzed")

        return PredictionResponse(
            status="success",
            data=predictions,
            summary=summary,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

    except ModelNotLoadedException as e:
        logger.error(f"Model error: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
    except ValidationException as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction failed. Please try again.")


@app.get(f"{settings.API_PREFIX}/info", tags=["Info"], response_model=APIInfoResponse)
async def info():
    """Get API information and configuration"""
    return APIInfoResponse(
        api_name=settings.API_TITLE,
        version=settings.API_VERSION,
        environment=settings.ENVIRONMENT,
        models=["15 Independent XGBoost Pipelines (6 Production, 9 Experimental)"],
        antibiotics=ANTIBIOTIC_COLS,
        input_fields={
            "Age": "float (0-150 years)",
            "Gender": "string (M or F)",
            "Souches": "string (bacterial strain)",
            "Diabetes": "string (Yes or No)",
            "Hypertension": "string (Yes or No)",
            "Hospital_before": "string (Yes or No)",
            "Infection_Freq": "float (≥ 0)",
        },
        endpoints={
            "health": f"{settings.API_PREFIX}/health",
            "predict": f"{settings.API_PREFIX}/predict",
            "info": f"{settings.API_PREFIX}/info",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
