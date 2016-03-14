# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
    (r'^', include('radiacion.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)