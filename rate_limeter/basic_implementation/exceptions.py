from fastapi import HTTPException
from typing import Dict, Any

class RateLimitExceededException(HTTPException):
    def __init__(self, algorithm:str, info:Dict[str, Any]):
        detail = {
            "error": "Rate limit exceeded",
            "algorithm": algorithm,
            "info": info
        }
        super().__init__(status_code = 429, detail = detail) 

class RateLimiterUnavailableException(Exception):
    def __init__(self, message: str = "Rate limiter service unavailable"):
        self.message = message
        super().__init__(self.message)

