"""Simple caching system for Theater Critics System."""

import hashlib
import json
import pickle
import time
from pathlib import Path
from typing import Any, Dict, Optional

from constants import (
    CACHE_FILE_EXTENSION,
    CACHE_HASH_DIGEST_SIZE,
    CACHE_MINIMUM_VALID_SCORE,
    DEFAULT_CACHE_TTL_SECONDS,
)
from logging_config import get_logger


class SimpleCache:
    """Simple file-based cache for analysis results."""

    def __init__(self, cache_dir: str = ".cache", ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS):
        """Initialize cache with directory and TTL.

        Args:
            cache_dir: Directory to store cache files
            ttl_seconds: Time to live for cache entries (default: 1 hour from constants)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_seconds = ttl_seconds
        self.logger = get_logger()

    def _generate_key(self, scene_data: Dict, critic_name: str) -> str:
        """Generate cache key from scene data and critic name."""
        # Create deterministic hash from scene data + critic
        cache_data = {
            "scene": scene_data,
            "critic": critic_name,
        }
        content = json.dumps(cache_data, sort_keys=True)
        return hashlib.blake2b(content.encode(), digest_size=CACHE_HASH_DIGEST_SIZE).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key."""
        return self.cache_dir / f"{cache_key}{CACHE_FILE_EXTENSION}"

    def get(self, scene_data: Dict, critic_name: str) -> Optional[Any]:
        """Get cached result if available and not expired.

        Args:
            scene_data: Scene data dictionary
            critic_name: Name of the critic

        Returns:
            Cached result or None if not found/expired
        """
        cache_key = self._generate_key(scene_data, critic_name)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            self.logger.debug(f"Cache miss for {critic_name}: {cache_key}")
            return None

        try:
            with open(cache_path, 'rb') as f:
                cache_entry = pickle.load(f)

            # Check if cache entry is expired
            if time.time() - cache_entry['timestamp'] > self.ttl_seconds:
                self.logger.debug(f"Cache expired for {critic_name}: {cache_key}")
                cache_path.unlink()  # Remove expired cache
                return None

            self.logger.info(f"Cache hit for {critic_name}: {cache_key}")
            return cache_entry['data']

        except Exception as e:
            self.logger.warning(f"Failed to read cache for {critic_name}: {str(e)}")
            # Remove corrupted cache file
            try:
                cache_path.unlink()
            except Exception:
                pass
            return None

    def set(self, scene_data: Dict, critic_name: str, result: Any) -> None:
        """Store result in cache.

        Args:
            scene_data: Scene data dictionary
            critic_name: Name of the critic
            result: Result to cache
        """
        cache_key = self._generate_key(scene_data, critic_name)
        cache_path = self._get_cache_path(cache_key)

        cache_entry = {
            'timestamp': time.time(),
            'data': result
        }

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_entry, f)
            self.logger.debug(f"Cached result for {critic_name}: {cache_key}")
        except Exception as e:
            self.logger.warning(f"Failed to cache result for {critic_name}: {str(e)}")

    def clear(self) -> None:
        """Clear all cache entries."""
        for cache_file in self.cache_dir.glob(f"*{CACHE_FILE_EXTENSION}"):
            try:
                cache_file.unlink()
            except Exception as e:
                self.logger.warning(f"Failed to delete cache file {cache_file}: {str(e)}")
        self.logger.info("Cache cleared")

    def cleanup_expired(self) -> int:
        """Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        removed_count = 0
        for cache_file in self.cache_dir.glob(f"*{CACHE_FILE_EXTENSION}"):
            try:
                with open(cache_file, 'rb') as f:
                    cache_entry = pickle.load(f)

                if time.time() - cache_entry['timestamp'] > self.ttl_seconds:
                    cache_file.unlink()
                    removed_count += 1

            except Exception:
                # Remove corrupted cache files
                cache_file.unlink()
                removed_count += 1

        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} expired cache entries")

        return removed_count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        cache_files = list(self.cache_dir.glob(f"*{CACHE_FILE_EXTENSION}"))
        total_size = sum(f.stat().st_size for f in cache_files)

        expired_count = 0
        for cache_file in cache_files:
            try:
                with open(cache_file, 'rb') as f:
                    cache_entry = pickle.load(f)
                if time.time() - cache_entry['timestamp'] > self.ttl_seconds:
                    expired_count += 1
            except Exception:
                expired_count += 1

        return {
            'total_entries': len(cache_files),
            'expired_entries': expired_count,
            'total_size_bytes': total_size,
            'cache_directory': str(self.cache_dir),
            'ttl_seconds': self.ttl_seconds
        }


# Global cache instance
_cache_instance = None


def get_cache() -> SimpleCache:
    """Get global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = SimpleCache()
    return _cache_instance


def cache_analysis_result(func):
    """Decorator to cache analysis results."""
    from functools import wraps

    @wraps(func)
    async def wrapper(self, scene, *args, **kwargs):
        # Create cache key from scene data and critic name
        scene_dict = {
            'title': scene.title,
            'musical': scene.musical,
            'description': scene.description,
            'lyrics': scene.lyrics,
            'stage_directions': scene.stage_directions,
            'character_notes': scene.character_notes
        }

        cache = get_cache()

        # Try to get from cache first
        cached_result = cache.get(scene_dict, self.name)
        if cached_result is not None:
            return cached_result

        # If not in cache, compute result
        result = await func(self, scene, *args, **kwargs)

        # Cache the result (only if successful)
        if (
            hasattr(result, 'scores') and 
            result.scores.overall >= CACHE_MINIMUM_VALID_SCORE and 
            not getattr(result, 'is_error', False)  # Ensure result is not an error
        ):
            cache.set(scene_dict, self.name, result)

        return result

    return wrapper
