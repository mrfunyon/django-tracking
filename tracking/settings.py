from django.conf import settings

USE_GEOIP = getattr(settings, 'TRACKING_USE_GEOIP', False)
GEOIP_CACHE_TYPE = getattr(settings, 'TRACKING_GEOIP_CACHE_TYPE', 4)
NO_TRACKING_PREFIXES = getattr(settings, 'TRACKING_EXCLUDE_PREFIXES', [])
TIMEOUT = getattr(settings, 'TRACKING_TIMEOUT', 10)
CLEANUP_TIMEOUT = getattr(settings, 'TRACKING_CLEANUP_TIMEOUT', 24)
DEFAULT_TEMPLATE = getattr(settings, 'TRACKING_DEFAULT_TEMPLATE', 'tracking/visitor_map.html' )
GOOGLE_MAPS_KEY = getattr(settings, 'TRACKING_GOOGLE_MAPS_KEY', None)




