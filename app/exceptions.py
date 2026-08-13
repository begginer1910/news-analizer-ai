class ServiceError(Exception):
    """Base exception for all external service errors."""
    pass

class NewsAPIError(ServiceError):
    """Error communicating with NewsAPI."""
    pass

class AIServiceError(ServiceError):
    """Error communicating with the AI service (Groq)."""
    pass

class ValidationError(ServiceError):
    """Input data validation error."""
    pass