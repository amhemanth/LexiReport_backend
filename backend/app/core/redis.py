"""Redis configuration and utilities."""
from typing import Optional, Any
import json
from redis import Redis, ConnectionPool
from redis.exceptions import RedisError, ConnectionError
from app.config.settings import get_settings
from app.core.logger import logger

settings = get_settings()

class RedisManager:
    """Redis connection manager."""
    
    _instance: Optional['RedisManager'] = None
    _pool: Optional[ConnectionPool] = None
    _client: Optional[Redis] = None
    _is_connected: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Redis connection."""
        if self._pool is None:
            try:
                self._pool = ConnectionPool.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                    retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
                    max_connections=settings.REDIS_MAX_CONNECTIONS
                )
                # Test connection
                test_client = Redis(connection_pool=self._pool)
                test_client.ping()
                self._is_connected = True
                logger.info("Redis connection pool created successfully")
            except Exception as e:
                logger.error(f"Failed to create Redis connection pool: {str(e)}")
                self._is_connected = False
                # Don't raise the exception, allow the application to start without Redis
                # The application will use in-memory fallbacks when Redis is not available

    @property
    def client(self) -> Redis:
        """Get Redis client instance."""
        if self._client is None and self._is_connected:
            try:
                self._client = Redis(connection_pool=self._pool)
                logger.info("Redis client created successfully")
            except Exception as e:
                logger.error(f"Failed to create Redis client: {str(e)}")
                self._is_connected = False
                raise
        return self._client

    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        if not self._is_connected:
            return False
        try:
            return self.client.ping()
        except Exception:
            self._is_connected = False
            return False

    def set_key(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Set a key-value pair in Redis.
        Args:
            key: The key to set
            value: The value to set (will be JSON serialized)
            expire: Optional expiration time in seconds
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Redis is not connected, operation skipped")
            return False

        try:
            serialized_value = json.dumps(value)
            if expire:
                return self.client.setex(key, expire, serialized_value)
            return self.client.set(key, serialized_value)
        except (RedisError, TypeError) as e:
            logger.error(f"Failed to set Redis key {key}: {str(e)}")
            return False

    def get_key(self, key: str) -> Optional[Any]:
        """
        Get a value from Redis.
        Args:
            key: The key to get
        Returns:
            The deserialized value or None if not found
        """
        if not self.is_connected():
            logger.warning("Redis is not connected, operation skipped")
            return None

        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Failed to get Redis key {key}: {str(e)}")
            return None

    def delete_key(self, key: str) -> bool:
        """
        Delete a key from Redis.
        Args:
            key: The key to delete
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Redis is not connected, operation skipped")
            return False

        try:
            return bool(self.client.delete(key))
        except RedisError as e:
            logger.error(f"Failed to delete Redis key {key}: {str(e)}")
            return False

    def increment_key(self, key: str, expire: Optional[int] = None) -> Optional[int]:
        """
        Increment a key's value in Redis.
        Args:
            key: The key to increment
            expire: Optional expiration time in seconds
        Returns:
            The new value or None if failed
        """
        if not self.is_connected():
            logger.warning("Redis is not connected, operation skipped")
            return None

        try:
            pipe = self.client.pipeline()
            pipe.incr(key)
            if expire:
                pipe.expire(key, expire)
            result = pipe.execute()
            return result[0]
        except RedisError as e:
            logger.error(f"Failed to increment Redis key {key}: {str(e)}")
            return None

    def check_connection(self) -> bool:
        """
        Check if Redis connection is working.
        Returns:
            bool: True if connection is working, False otherwise
        """
        return self.is_connected()

# Create a singleton instance
redis_manager = RedisManager()

def get_redis_client() -> Redis:
    """Get Redis client instance."""
    return redis_manager.client 