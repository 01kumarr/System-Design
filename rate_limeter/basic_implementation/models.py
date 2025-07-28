from pydantic import BaseModel
from enum import Enum
from typing import Optional, Any, Dict

class RateLimitType(str, Enum):
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket" 

class RateLimitConfig(BaseModel):
    capacity:int
    rate:int
    Window_seconds:int

class RateLimitResult(BaseModel):
    allowed: bool
    remaining: int
    capacity: int
    reset_time: Optional[float] = None
    current_level: Optional[int] = None
    algorithm: str

class RateLimitError(BaseModel):
    error: str
    message: str
    algorithm: Optional[str] = None
    info: Dict[str, Any] = {}


