from django.shortcuts import get_object_or_404
from .models import ShortenedURL
from .models import Click
from django.db.models import Count


def get_user_urls(user):
    return ShortenedURL.objects.filter(owner=user)


def get_user_url_by_id(user, pk):
    queryset = get_user_urls(user)
    return get_object_or_404(queryset, pk=pk)


def get_url_by_short_code(short_code):
    return get_object_or_404(ShortenedURL, short_code=short_code)


def get_url_analytics(user, url_id=None):
    """
    Returns clicks for a specific URL or all URLs owned by the user.
    """
    queryset = Click.objects.filter(url__owner=user).order_by('-clicked_at')
    if url_id:
        queryset = queryset.filter(url_id=url_id)
    return queryset



def get_url_detailed_analytics(url_instance):
    # 1. Total Clicks
    total_clicks = url_instance.clicks.count()

    # 2. Clicks by Country
    country_stats = url_instance.clicks.values('country').annotate(
        count=Count('id')
    ).order_by('-count')

    browser_stats = url_instance.clicks.values('user_agent').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    return {
        "total_clicks": total_clicks,
        "country_stats": country_stats,
        "browser_stats": browser_stats,
    }