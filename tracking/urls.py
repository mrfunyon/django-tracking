from django.conf.urls.defaults import *
from tracking.settings import USE_GEOIP
from tracking import views

urlpatterns = patterns('',
    url(r'^refresh/$', views.update_active_users, name='tracking-refresh-active-users'),
    url(r'^refresh/json/$', views.get_active_users, name='tracking-get-active-users'),
)

if USE_GEOIP:
    urlpatterns += patterns('',
        url(r'^map/$', views.display_map, name='tracking-visitor-map'),
    )
