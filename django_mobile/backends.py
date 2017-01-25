from django.utils.encoding import smart_str
from django_mobile.conf import settings


class SessionBackend(object):
    def get(self, request, default=None):
        return request.session.get(settings.FLAVOURS_SESSION_KEY, default)

    def set(self, request, flavour):
        request.session[settings.FLAVOURS_SESSION_KEY] = flavour

    def save(self, request, response):
        pass


class CookieBackend(object):
    def get(self, request, default=None):
        return request.COOKIES.get(settings.FLAVOURS_COOKIE_KEY, default)

    def set(self, request, flavour):
        request.COOKIES[settings.FLAVOURS_COOKIE_KEY] = flavour
        request._flavour_cookie = flavour

    def save(self, request, response):
        if hasattr(request, '_flavour_cookie'):
            response.set_cookie(
                smart_str(settings.FLAVOURS_COOKIE_KEY),
                smart_str(request._flavour_cookie),
                httponly=settings.FLAVOURS_COOKIE_HTTPONLY)