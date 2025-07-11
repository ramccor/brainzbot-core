from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'(?P<year>\d{4})-(?P<month>0[1-9]|1[0-2])-(?P<day>0[1-9]|[1-2][0-9]|3[0-1])/$',
            views.DayLogViewer.as_view(), name="log_day"),
    re_path(r'(?P<year>\d{4})-(?P<month>0[1-9]|1[0-2])-(?P<day>0[1-9]|[1-2][0-9]|3[0-1]).log$',
            views.DayLogViewer.as_view(format='text'), name="log_day_text"),
    re_path(r'^missed/(?P<nick>[\w\-\|]*)/$', views.MissedLogViewer.as_view(),
            name="log_missed"),
    re_path(r'^msg/(?P<msg_pk>\d+)/$', views.SingleLogViewer.as_view(),
            name="log_message_permalink"),
    re_path(r'^search/$', views.SearchLogViewer.as_view(), name='log_search'),
    re_path(r'^help/$', views.Help.as_view(), name='help_bot'),
    re_path(r'^stream/$', views.LogStream.as_view(), name='log_stream'),
    re_path(r'^$', views.DayLogViewer.as_view(),
            name="log_current"),
]
