import redis
import functools
import json
import asyncio
import inspect
from utils.observer import Event
from utils.logger import logger

# Redis connection
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Metrics keys
CACHE_HITS_KEY = "metrics:cache_hits"
CACHE_MISSES_KEY = "metrics:cache_misses"

# Cache miss event
cache_miss_event = Event()


def redis_cache(ttl=60):
    """
    Decorator for caching sync or async functions in Redis.
    """
    def decorator(func):
        is_async = inspect.iscoroutinefunction(func)  # ✅ updated here

        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                key = f"{func.__name__}:{args}:{tuple(kwargs.items())}"
                logger.info(f"redis_cache executed for key: {key}")

                # Try fetching from cache
                try:
                    cached = r.get(key)
                    if cached:
                        try:
                            r.incr(CACHE_HITS_KEY)
                        except Exception as e:
                            logger.warning(f"Failed to increment cache hits: {e}")
                        return json.loads(cached)
                except Exception as e:
                    logger.warning(f"Redis GET failed: {e}")

                # Cache miss
                try:
                    r.incr(CACHE_MISSES_KEY)
                except Exception as e:
                    logger.warning(f"Failed to increment cache misses: {e}")
                cache_miss_event.notify(f"Cache miss for key: {key}")

                # Execute the actual function
                result = await func(*args, **kwargs)

                # Store in cache
                try:
                    r.setex(key, ttl, json.dumps(result))
                except TypeError:
                    logger.warning("Result not JSON serializable, storing as string")
                    try:
                        r.setex(key, ttl, str(result))
                    except Exception as e:
                        logger.error(f"Redis SETEX failed: {e}")
                except Exception as e:
                    logger.error(f"Redis SETEX failed: {e}")

                return result

            return async_wrapper

        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                key = f"{func.__name__}:{args}:{tuple(kwargs.items())}"
                logger.info(f"redis_cache executed for key: {key}")

                # Try fetching from cache
                try:
                    cached = r.get(key)
                    if cached:
                        try:
                            r.incr(CACHE_HITS_KEY)
                        except Exception as e:
                            logger.warning(f"Failed to increment cache hits: {e}")
                        return json.loads(cached)
                except Exception as e:
                    logger.warning(f"Redis GET failed: {e}")

                # Cache miss
                try:
                    r.incr(CACHE_MISSES_KEY)
                except Exception as e:
                    logger.warning(f"Failed to increment cache misses: {e}")
                cache_miss_event.notify(f"Cache miss for key: {key}")

                # Execute the actual function
                result = func(*args, **kwargs)

                # Store in cache
                try:
                    r.setex(key, ttl, json.dumps(result))
                except TypeError:
                    logger.warning("Result not JSON serializable, storing as string")
                    try:
                        r.setex(key, ttl, str(result))
                    except Exception as e:
                        logger.error(f"Redis SETEX failed: {e}")
                except Exception as e:
                    logger.error(f"Redis SETEX failed: {e}")

                return result

            return sync_wrapper

    return decorator
