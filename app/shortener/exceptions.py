from rest_framework.exceptions import APIException
from rest_framework import status


class URLExpiredException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "URL expired or max clicks reached"
    default_code = "url_expired"


class URLNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Short URL not found"
    default_code = "url_not_found"


class AliasAlreadyExistsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Custom alias already exists"
    default_code = "alias_exists"
