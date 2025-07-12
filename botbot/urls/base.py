from django.conf import settings
from django.urls import re_path, include
from django.shortcuts import render

from botbot.apps.bots.views import ChannelList
from botbot.apps.preview.views import LandingPage

channel_patterns = [
    re_path(r'', include('botbot.apps.logs.urls')),
]

urlpatterns = [
    re_path(r'^$', LandingPage.as_view()),
    re_path(r'^sitemap\.xml', include('botbot.apps.sitemap.urls')),
    re_path(r'^(?P<bot_slug>[\-\w\:\.]+(\@[\w]+)?)/(?P<channel_slug>[\-\w\.]+)/',
            include(channel_patterns)),
    re_path(r'^(?P<network_slug>[\-\w\.]+)/$', ChannelList.as_view())
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^404/$', lambda r: render(r, template_name='404.html')),
        re_path(r'^500/$', lambda r: render(r, template_name='500.html')),
    ]
