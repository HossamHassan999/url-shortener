from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .serializers import ShortenedURLSerializer
from .selectors import get_user_urls, get_user_url_by_id
from .servicess.url_services import URLService
from .servicess.cache_service import CacheService
from config.responses import success_response
from .serializers import ClickSerializer
from .selectors import get_url_analytics

class ShortenedURLViewSet(viewsets.ViewSet):
    serializer_class = ShortenedURLSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        page_number = request.query_params.get("page", 1)
        cache_key = f"user:{request.user.id}:urls:page:{page_number}"

        # 1. Try to get from Redis
        cached_data = CacheService.get(cache_key)
        if cached_data:
            return success_response(data=cached_data, message="URLs retrieved (cache)")

        # 2. Database fallback
        urls = get_user_urls(request.user)
        paginator = PageNumberPagination()
        paginator.page_size = 5
        
        paginated_queryset = paginator.paginate_queryset(urls, request)
        serializer = self.serializer_class(paginated_queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data).data       
        # 3. Store in Redis for 1 minute
        CacheService.set(cache_key, paginated_data, timeout=60)  

        return success_response(data=paginated_data, message="URLs retrieved successfully")

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        url = URLService.create_short_url(
            user=request.user,
            serializer=serializer,
            custom_alias=request.data.get("custom_alias")
        )

        # 4. Invalidate all pages in Redis for this user
        CacheService.invalidate_user_cache(request.user.id)

        return success_response(
            data=self.serializer_class(url).data,
            message="Short URL created",
            status_code=201
        )

    def retrieve(self, request, pk=None):
        url = get_user_url_by_id(request.user, pk)
        serializer = self.serializer_class(url)
        return success_response(data=serializer.data, message="URL retrieved successfully")

    def destroy(self, request, pk=None):
        url = get_user_url_by_id(request.user, pk)
        URLService.delete_url(url)
        
        # 5. Invalidate all pages in Redis for this user
        CacheService.invalidate_user_cache(request.user.id)

        return success_response(
            message="URL deleted successfully",
            status_code=204
        )

    @action(detail=False, methods=["get"], url_path="redirect/(?P<short_code>[^/.]+)")
    def redirect_url(self, request, short_code=None):
        # Public redirection logic
        return URLService.process_redirect(short_code, request)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        # 1. Get the URL object
        url_instance = get_user_url_by_id(request.user, pk)
        
        # 2. Check Cache first (Analytics keys are perfect for caching)
        cache_key = f"url_analytics:{pk}"
        cached_analytics = CacheService.get(cache_key)
        if cached_analytics:
            return success_response(data=cached_analytics, message="Detailed analytics (cache)")

        # 3. Get detailed stats from selector
        from .selectors import get_url_detailed_analytics
        stats = get_url_detailed_analytics(url_instance)

        # 4. Save to Cache for 5 minutes (Analytics don't need to be real-time every second)
        CacheService.set(cache_key, stats, timeout=300)

        return success_response(data=stats, message="Detailed analytics retrieved")


class ClickAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing URL analytics.
    Only allows LIST and RETRIEVE.
    """
    serializer_class = ClickSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show clicks for URLs owned by the current user
        user = self.request.user
        url_id = self.request.query_params.get('url_id')
        
        # We reuse our selector logic
        return get_url_analytics(user=user, url_id=url_id)
    