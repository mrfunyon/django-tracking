from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch

def get_notracking_urls():
  prefixes = getattr( settings, 'TRACKING_EXCLUDE_PREFIXES', [] )
  if ( settings.MEDIA_URL
       and settings.MEDIA_URL != '/'
       and ( not settings.MEDIA_URL in prefixes ) ):
    prefixes.append( settings.MEDIA_URL )

  if ( settings.ADMIN_MEDIA_PREFIX
       and ( not settings.ADMIN_MEDIA_PREFIX in prefixes ) ):
    prefixes.append( settings.ADMIN_MEDIA_PREFIX )

  try:
    prefixes.append( reverse('tracking-refresh-active-users') )
  except NoReverseMatch:
    # django-tracking hasn't been included in the URLconf if we get here
    pass

  return prefixes


USE_GEOIP = getattr(settings, 'TRACKING_USE_GEOIP', False)

GEOIP_CACHE_TYPE = getattr(settings, 'TRACKING_GEOIP_CACHE_TYPE', 4)

NO_TRACKING_PREFIXES = get_notracking_urls()

TIMEOUT = getattr(settings, 'TRACKING_TIMEOUT', 10)

CLEANUP_TIMEOUT = getattr(settings, 'TRACKING_CLEANUP_TIMEOUT', 24)

DEFAULT_TEMPLATE = getattr( settings, 'TRACKING_DEFAULT_TEMPLATE', 'tracking/visitor_map.html' )

GOOGLE_MAPS_KEY = getattr(settings, 'TRACKING_GOOGLE_MAPS_KEY', None)




