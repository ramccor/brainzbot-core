from django.contrib import admin
from django.urls import include, re_path

admin.autodiscover()

urlpatterns = [
    re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    re_path(r'^admin/', admin.site.urls),
]
