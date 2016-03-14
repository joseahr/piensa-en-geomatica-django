# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('radiacion.views',
    url(r'^radiacion/$', 'radiacion', name='rad'),
)