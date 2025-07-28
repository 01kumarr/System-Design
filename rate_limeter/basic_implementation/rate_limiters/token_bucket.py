import time 
import json 
from typing import Tuple

from basic_implementation.database import redis_client 
from basic_implementation.models import RateLimitConfig, RateLimitResult
from .base import BaseRateLimiter 


class TokenBucketRateLimiter(BaseRateLimiter):
    def __init__(self, config: RateLimitConfig):
        super().__init__(config)

    def get_algorithm_name(self) -> str:
        return "token_bucket"
    
    def is_allowed(self, key: str) -> Tuple[bool, RateLimitResult]:
        "Check if the request is allowed using token bucket algorithm"
        bucket_key = f"token_bucket:{key}"
        current_time = time.time() 

        try:
            bucket_data = redis_client.get(bucket_key)

            if bucket_data:
                bucket = json.loads(bucket_data) # type: ignore
                last_refill = bucket['last_refill']
                tokens = bucket['tokens']

            else:
                last_refill = current_time
                tokens = self.config.capacity 

            ## calculate elapsed time since last refill 
            time_elapsed = current_time - last_refill 
            tokens_to_add = (time_elapsed / self.config.Window_seconds) * self.config.rate 
            tokens = min(self.config.capacity, tokens + tokens_to_add)

            if tokens >= 1:
                tokens -= 1
                allowed = True
            else:
                allowed = False 

            bucket_state = {
                'tokens': tokens,
                'last_refill': current_time,
                'capacity': self.config.capacity
            }

            redis_client.setex(
                bucket_key, 
                self.config.Window_seconds * 2, 
                json.dumps(bucket_state)
            )

            result = RateLimitResult(
                allowed=allowed,
                remaining=int(tokens),
                capacity=self.config.capacity,
                reset_time=current_time + (self.config.capacity - tokens) / (self.config.rate / self.config.Window_seconds),
                algorithm=self.get_algorithm_name()
            )

            return allowed, result 
        except Exception as e:
            result = RateLimitResult(
                allowed=True,
                remaining=self.config.capacity,
                capacity=self.config.capacity,
                algorithm=self.get_algorithm_name()
            )

            return True, result
        
