import time
import json
from typing import Tuple
from ..database import redis_client
from ..models import RateLimitConfig, RateLimitResult
from .base import BaseRateLimiter

class LeakyBucketRateLimiter(BaseRateLimiter):
    def __init__(self, config: RateLimitConfig):
        super().__init__(config)
    
    def get_algorithm_name(self) -> str:
        return "leaky_bucket"
    
    def is_allowed(self, key: str) -> Tuple[bool, RateLimitResult]:
        """Check if request is allowed using leaky bucket algorithm"""
        bucket_key = f"leaky_bucket:{key}"
        current_time = time.time()
        
        try:
            # Get current bucket state
            bucket_data = redis_client.get(bucket_key)
            
            if bucket_data:
                bucket = json.loads(bucket_data) # type: ignore
                last_leak = bucket['last_leak']
                current_level = bucket['level']
            else:
                # Initialize bucket
                last_leak = current_time
                current_level = 0
            
            # Calculate how much has leaked since last check
            time_elapsed = current_time - last_leak
            leaked_amount = (time_elapsed / self.config.Window_seconds) * self.config.rate
            current_level = max(0, current_level - leaked_amount)
            
            # Check if bucket has capacity
            if current_level < self.config.capacity:
                current_level += 1
                allowed = True
            else:
                allowed = False
            
            # Update bucket state
            bucket_state = {
                'level': current_level,
                'last_leak': current_time,
                'capacity': self.config.capacity
            }
            
            redis_client.setex(
                bucket_key, 
                self.config.Window_seconds * 2, 
                json.dumps(bucket_state)
            )
            
            result = RateLimitResult(
                allowed=allowed,
                remaining=int(self.config.capacity - current_level),
                capacity=self.config.capacity,
                current_level=int(current_level),
                algorithm=self.get_algorithm_name()
            )
            
            return allowed, result
            
        except Exception as e:
            # Fail open - allow request if Redis is down
            result = RateLimitResult(
                allowed=True,
                remaining=self.config.capacity,
                capacity=self.config.capacity,
                current_level=0,
                algorithm=self.get_algorithm_name()
            )
            return True, result