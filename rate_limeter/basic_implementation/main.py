from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from .config import settings
from .database import RedisClient
from .middleware import TokenBucketDependency, LeakyBucketDependency, rate_limit_manager
from .models import RateLimitType, RateLimitResult
from .exceptions import RateLimitExceededException
from .utils import ClientIndetifier
import time

# Create FastAPI application
app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    debug=settings.debug
)

@app.exception_handler(RateLimitExceededException)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceededException):
    """Handle rate limit exceeded exceptions"""
    return JSONResponse(
        status_code=429,
        content=exc.detail,
        headers={"Retry-After": "60"}
    )

@app.get("/api/v1/token-bucket")
async def token_bucket_endpoint(
    request: Request,
    rate_info: RateLimitResult = TokenBucketDependency
):
    """Endpoint with token bucket rate limiting"""
    return {
        "message": "Request processed with Token Bucket rate limiting",
        "client_key": ClientIndetifier.hash_key(
            ClientIndetifier.generate_key(request)
        ),
        "rate_limit_info": rate_info.dict(),
        "timestamp": time.time()
    }

@app.get("/api/v1/leaky-bucket")
async def leaky_bucket_endpoint(
    request: Request,
    rate_info: RateLimitResult = LeakyBucketDependency
):
    """Endpoint with leaky bucket rate limiting"""
    return {
        "message": "Request processed with Leaky Bucket rate limiting",
        "client_key": ClientIndetifier.hash_key(
            ClientIndetifier.generate_key(request)
        ),
        "rate_limit_info": rate_info.dict(),
        "timestamp": time.time()
    }

@app.get("/api/v1/status")
async def get_rate_limit_status(request: Request):
    """Get current rate limit status for client"""
    client_key = ClientIndetifier.generate_key(request)
    
    # Get status for both algorithms
    token_allowed, token_result = rate_limit_manager.token_bucket.is_allowed(client_key)
    leaky_allowed, leaky_result = rate_limit_manager.leaky_bucket.is_allowed(client_key)
    
    return {
        "client_key": ClientIndetifier.hash_key(client_key),
        "token_bucket": {
            "allowed": token_allowed,
            "info": token_result.dict()
        },
        "leaky_bucket": {
            "allowed": leaky_allowed,
            "info": leaky_result.dict()
        },
        "timestamp": time.time()
    }

@app.get("/")
async def health_check():
    """Health check endpoint"""
    redis_status = "healthy" if RedisClient.ping() else "unhealthy"
    
    return {
        "status": "healthy",
        "redis": redis_status,
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)