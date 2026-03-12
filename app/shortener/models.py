import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator
from datetime import timedelta
from django.utils import timezone


def get_default_expiry():
    return timezone.now() + timedelta(days=30)

class ShortenedURL(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=10, unique=True)
    custom_alias = models.CharField(max_length=50, blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="urls")
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(default=get_default_expiry)
    max_clicks = models.PositiveIntegerField(default=10000)
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.short_code

    def is_expired(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        if self.max_clicks and self.click_count >= self.max_clicks:
            return True
        return False

class Click(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.ForeignKey(ShortenedURL, on_delete=models.CASCADE, related_name="clicks")
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    clicked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Click on {self.url.short_code} at {self.clicked_at}"
