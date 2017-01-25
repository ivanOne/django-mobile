# -*- coding: utf-8 -*-

__author__ = u'Gregor Müllegger'
__version__ = '0.7.0.dev1'

import importlib
import threading
from django.core.exceptions import ImproperlyConfigured
from django_mobile.conf import settings


_local = threading.local()


class ProxyBackend(object):
    def get_backend(self):
        backend = settings.FLAVOURS_STORAGE_BACKEND
        if not settings.FLAVOURS_STORAGE_BACKEND:
            raise ImproperlyConfigured(
                u"You must specify a FLAVOURS_STORAGE_BACKEND setting to "
                u"save the flavour for a user.")
        return importlib.import_module(settings.FLAVOURS_STORAGE_BACKEND)()

    def get(self, *args, **kwargs):
        if settings.FLAVOURS_STORAGE_BACKEND is None:
            return None
        return self.get_backend().get(*args, **kwargs)

    def set(self, *args, **kwargs):
        if settings.FLAVOURS_STORAGE_BACKEND is None:
            return None
        return self.get_backend().set(*args, **kwargs)

    def save(self, *args, **kwargs):
        if settings.FLAVOURS_STORAGE_BACKEND is None:
            return None
        return self.get_backend().save(*args, **kwargs)


flavour_storage = ProxyBackend()


def get_flavour(request=None, default=None):
    flavour = None
    request = request or getattr(_local, 'request', None)
    # get flavour from storage if enabled
    if request:
        flavour = flavour_storage.get(request)
    # check if flavour is set on request
    if not flavour and hasattr(request, 'flavour'):
        flavour = request.flavour
    # if set out of a request-response cycle its stored on the thread local
    if not flavour:
        flavour = getattr(_local, 'flavour', default)
    # if something went wrong we return the very default flavour
    if flavour not in settings.FLAVOURS:
        flavour = settings.FLAVOURS[0]
    return flavour


def set_flavour(flavour, request=None, permanent=False):
    if flavour not in settings.FLAVOURS:
        raise ValueError(
            u"'%r' is no valid flavour. Allowed flavours are: %s" % (
                flavour,
                ', '.join(settings.FLAVOURS),))
    request = request or getattr(_local, 'request', None)
    if request:
        request.flavour = flavour
        if permanent:
            flavour_storage.set(request, flavour)
    elif permanent:
        raise ValueError(
            u'Cannot set flavour permanently, no request available.')
    _local.flavour = flavour


def _set_request_header(request, flavour):
    request.META['HTTP_X_FLAVOUR'] = flavour


def _init_flavour(request):
    _local.request = request
    if hasattr(request, 'flavour'):
        _local.flavour = request.flavour
    if not hasattr(_local, 'flavour'):
        _local.flavour = settings.FLAVOURS[0]
