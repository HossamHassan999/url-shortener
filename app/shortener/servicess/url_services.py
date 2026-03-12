from django.shortcuts import redirect
from django.db import transaction

from ..models import ShortenedURL, Click
from ..utils import generate_short_code
from ..selectors import get_url_by_short_code
from ..exceptions import URLExpiredException, AliasAlreadyExistsException


class URLService:

    @staticmethod
    @transaction.atomic
    def create_short_url(*, user, serializer, custom_alias=None):

        if custom_alias:
            if ShortenedURL.objects.filter(short_code=custom_alias).exists():
                raise AliasAlreadyExistsException()

            short_code = custom_alias
        else:
            short_code = generate_short_code()

        return serializer.save(
            owner=user,
            short_code=short_code,
            custom_alias=custom_alias
        )

    @staticmethod
    def delete_url(url):
        url.delete()

    @staticmethod
    @transaction.atomic
    def process_redirect(short_code, request):

        url = get_url_by_short_code(short_code)

        if url.is_expired():
            raise URLExpiredException()

        url.click_count += 1
        url.save(update_fields=["click_count"])

        Click.objects.create(
            url=url,
            ip_address=request.META.get("REMOTE_ADDR", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            referrer=request.META.get("HTTP_REFERER", "")
            
        )

        return redirect(url.original_url)
