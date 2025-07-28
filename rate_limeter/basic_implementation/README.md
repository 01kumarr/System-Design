# Basic Rate Limiter with FastAPI and Redis

A simple rate limiting implementation using FastAPI and Redis, featuring Token Bucket and Leaky Bucket algorithms with clean modular architecture.

## 🚀 Features

- **Token Bucket Algorithm**: Allows burst traffic, refills at steady rate
- **Leaky Bucket Algorithm**: Smooths traffic by processing at constant rate
- **FastAPI Integration**: Easy-to-use dependencies for endpoint protection
- **Redis Backend**: Fast and persistent rate limiting storage
- **Modular Architecture**: Clean separation of concerns
- **Graceful Degradation**: Fail-open when Redis unavailable

## 🛠️ Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Start Redis server**:
```bash
# Using Docker
docker run -d -p 6379:6379 redis:latest
```

3. **Run the application**:
```bash
python main.py
```

## 📁 Project Structure

```
basic_rate_limiter/
├── config.py              # Configuration and settings
├── database.py            # Redis client management
├── models.py              # Pydantic models
├── exceptions.py          # Custom exceptions
├── utils.py               # Utility functions
├── rate_limiters/         # Rate limiting algorithms
│   ├── base.py           # Abstract base class
│   ├── token_bucket.py   # Token bucket implementation
│   └── leaky_bucket.py   # Leaky bucket implementation
├── middleware.py          # Rate limiting middleware
└── main.py               # FastAPI application
```

## 🔧 Configuration

Create `.env` file (optional):
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
DEFAULT_CAPACITY=10        # Max requests in bucket
DEFAULT_REFILL_RATE=5      # Requests per minute
DEFAULT_WINDOW_SECONDS=60  # Time window
```

## 🎯 Usage

### API Endpoints

```bash
# Token bucket endpoint
curl http://localhost:8000/api/v1/token-bucket

# Leaky bucket endpoint
curl http://localhost:8000/api/v1/leaky-bucket

# Check rate limit status
curl http://localhost:8000/api/v1/status

# Health check
curl http://localhost:8000/health
```

### Custom Implementation

```python
from basic_rate_limiter.models import RateLimitConfig
from basic_rate_limiter.rate_limiters import TokenBucketRateLimiter

# Create custom rate limiter
config = RateLimitConfig(capacity=50, rate=25, window_seconds=60)
limiter = TokenBucketRateLimiter(config)

# Check if request allowed
allowed, result = limiter.is_allowed("client_key")
```

### FastAPI Dependencies

```python
from basic_rate_limiter.middleware import TokenBucketDependency

@app.get("/protected")
async def protected_route(rate_info = TokenBucketDependency):
    return {"message": "Success", "rate_info": rate_info}
```

## 📊 Response Format

**Success Response**:
```json
{
  "message": "Request processed",
  "rate_limit_info": {
    "allowed": true,
    "remaining": 7,
    "capacity": 10,
    "algorithm": "token_bucket"
  }
}
```

**Rate Limited (HTTP 429)**:
```json
{
  "error": "Rate limit exceeded",
  "algorithm": "token_bucket",
  "info": {
    "remaining": 0,
    "capacity": 10,
    "reset_time": 1640995200.0
  }
}
```

## 🔄 How It Works

**Token Bucket**: Bucket fills with tokens at steady rate. Each request consumes a token. Allows bursts up to capacity.

**Leaky Bucket**: Requests fill bucket, leak out at constant rate. Smooths traffic and prevents bursts.

## 🛡️ Error Handling

- **Redis Down**: Fails open (allows all requests)
- **Rate Exceeded**: Returns HTTP 429 with retry info
- **Invalid Config**: Raises configuration exceptions

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | localhost | Redis hostname |
| `REDIS_PORT` | 6379 | Redis port |
| `DEFAULT_CAPACITY` | 10 | Bucket capacity |
| `DEFAULT_REFILL_RATE` | 5 | Refill rate per minute |

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.
