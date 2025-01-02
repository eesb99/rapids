"""Utility functions for Redis caching in the ArXiv paper manager."""
import json
from typing import Any, Optional
import redis

def get_redis_client(config: dict) -> redis.Redis:
    """Create a Redis client from configuration."""
    return redis.Redis(**config)

def cache_get(client: redis.Redis, key: str) -> Optional[Any]:
    """Get a value from cache, returning None if not found."""
    value = client.get(key)
    return json.loads(value) if value else None

def cache_set(client: redis.Redis, key: str, value: Any) -> None:
    """Set a value in cache with JSON serialization."""
    client.set(key, json.dumps(value))

def generate_cache_key(prefix: str, *args) -> str:
    """Generate a cache key from prefix and arguments."""
    return f"{prefix}:" + ":".join(str(arg) for arg in args)
