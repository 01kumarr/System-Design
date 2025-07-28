from fastapi import Request, Depends
from typing import Optional
from .models import RateLimitType, RateLimitConfig, RateLimitResult
from .rate_limiters import TokenBucketRateLimiter, LeakyBucketRateLimiter
from .utils import ClientIndetifier
from .exceptions import RateLimitExceededException
from .config import settings

class RateLimitManager:
    def __init__(self):
        self.default_config = RateLimitConfig(
            capacity=settings.default_capacity,
            rate=settings.default_refile_rate, 
            Window_seconds=settings.default_window_seconds
        )
        
        self.token_bucket = TokenBucketRateLimiter(self.default_config)
        self.leaky_bucket = LeakyBucketRateLimiter(self.default_config)
    
    def get_limiter(self, limiter_type: RateLimitType):
        """Get rate limiter instance by type"""
        if limiter_type == RateLimitType.TOKEN_BUCKET:
            return self.token_bucket
        elif limiter_type == RateLimitType.LEAKY_BUCKET:
            return self.leaky_bucket
        else:
            raise ValueError(f"Unknown limiter type: {limiter_type}")
    
    def check_rate_limit(
        self, 
        request: Request, 
        limiter_type: RateLimitType,
        user_id: Optional[str] = None
    ) -> RateLimitResult:
        """Check rate limit for request"""
        key = ClientIndetifier.generate_key(request, user_id)
        limiter = self.get_limiter(limiter_type)
        
        allowed, result = limiter.is_allowed(key)
        
        if not allowed:
            raise RateLimitExceededException(
                algorithm=result.algorithm,
                info=result.dict()
            )
        
        return result

# Global rate limit manager
rate_limit_manager = RateLimitManager()

def create_rate_limit_dependency(limiter_type: RateLimitType):
    """Create a rate limiting dependency"""
    def rate_limit_dependency(request: Request) -> RateLimitResult:
        return rate_limit_manager.check_rate_limit(request, limiter_type)
    
    return rate_limit_dependency

# Common dependencies
TokenBucketDependency = Depends(create_rate_limit_dependency(RateLimitType.TOKEN_BUCKET))
LeakyBucketDependency = Depends(create_rate_limit_dependency(RateLimitType.LEAKY_BUCKET))
