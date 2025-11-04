import os
import redis
import json
from dotenv import load_dotenv

load_dotenv()

# Get Redis URL or default to local
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create Redis client
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# ===== Basic Utility Functions =====

def get_cache(key: str):
    """Retrieve cached value for a given key (returns dict or None)."""
    value = redis_client.get(key)
    if value:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return None


def set_cache(key: str, data, ttl: int = 3600):
    """Store a value in Redis with an optional TTL (in seconds)."""
    redis_client.setex(key, ttl, json.dumps(data))


def clear_cache(key: str):
    """Delete a cache key."""
    redis_client.delete(key)
