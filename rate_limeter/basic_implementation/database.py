import redis 
from typing import Optional
from .config import settings

class RedisClient:
    _instance: Optional['RedisClient'] = None 

    @classmethod
    def get_instance(cls) -> redis.Redis:
        if cls._instance is None:
            cls_instance = redis.Redis(
                host = settings.redis_host,
                port = settings.redis_port,
                db = settings.redis_db, 
                password = settings.resids_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
        return cls._instance  # type: ignore
    
    @classmethod 
    def ping(cls) -> bool:
        "check if the Redis server is reachable"
        try:
            client = cls.get_instance()
            return client.ping() # type: ignore
        except Exception as e:
            print(f"Redis ping failed: {e}")
            return False
        

# create a global Redis client instance
redis_client = RedisClient.get_instance()

