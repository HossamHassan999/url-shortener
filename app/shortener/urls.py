# shortener/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShortenedURLViewSet , ClickAnalyticsViewSet

router = DefaultRouter() # ClickAnalyticsViewSet
router.register(r'urls', ShortenedURLViewSet, basename='shortened-url')
router.register(r'clicks', ClickAnalyticsViewSet, basename='analytics-url')


urlpatterns = [
    path('', include(router.urls)),
]
