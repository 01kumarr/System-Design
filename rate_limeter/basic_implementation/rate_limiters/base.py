from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
from basic_implementation.models import RateLimitConfig, RateLimitResult 

class BaseRateLimiter(ABC):
    def __init__(self, config: RateLimitConfig):
        self.config = config

    @abstractmethod
    def is_allowed(self, key: str) -> Tuple[bool, RateLimitResult]:
        "Check if the request is allowed"
        pass 

    @abstractmethod
    def get_algorithm_name(self) -> str:
        "Get algorithm name"
        pass 

