from rest_framework import serializers
from .models import ShortenedURL, Click
import re
class ShortenedURLSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = ShortenedURL
        fields = '__all__'
        read_only_fields = ('short_code', 'click_count', 'created_at')

    def validate_custom_alias(self, value):
        if value:
            # Check for alphanumeric and hyphens only
            if not re.match(r'^[\w-]+$', value):
                raise serializers.ValidationError("Alias must contain only letters, numbers, and hyphens.")
        
class ClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = Click
        fields = '__all__'
