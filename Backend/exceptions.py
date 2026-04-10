"""Custom exceptions for the API"""


class APIException(Exception):
    """Base API exception"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ModelNotLoadedException(APIException):
    """Raised when model fails to load"""

    def __init__(self, message: str = "ML models not loaded"):
        super().__init__(message, status_code=503)


class PredictionException(APIException):
    """Raised when prediction fails"""

    def __init__(self, message: str = "Prediction failed"):
        super().__init__(message, status_code=400)


class ValidationException(APIException):
    """Raised when input validation fails"""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)


class InternalServerException(APIException):
    """Raised for unexpected server errors"""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500)
