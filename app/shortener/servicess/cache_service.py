from django.core.cache import cache

class CacheService:
    @staticmethod
    def get(key):
        return cache.get(key)

    @staticmethod
    def set(key, value, timeout=300):
        cache.set(key, value, timeout)

    @staticmethod
    def delete(key):
        cache.delete(key)

    @staticmethod
    def invalidate_user_cache(user_id):
        """
        Since you are using Redis, delete_pattern is the most efficient way.
        It removes all pages (page:1, page:2, etc.) for this specific user at once.
        """
        pattern = f"user:{user_id}:urls:page:*"
        # This will work perfectly with django-redis
        cache.delete_pattern(pattern)