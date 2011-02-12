import listeners
VERSION = (0, 3, 9)

def get_version():
    "Returns the version as a human-format string."
    return '.'.join([str(i) for i in VERSION])


try:
  from django.conf import settings
  prefixes = getattr( settings, 'TRACKING_EXCLUDE_PREFIXES', [] )
except ImportError:
  pass
else:
  if '!!!initialized!!!' not in prefixes:
    from django.core.urlresolvers import reverse, NoReverseMatch
    try:
      self_url = reverse('tracking-refresh-active-users')
      if not self_url in prefixes:
        prefixes.append( prefixes )
    except NoReverseMatch:
      # django-tracking hasn't been included in the URLconf if we get here
      pass

    if ( settings.MEDIA_URL
         and settings.MEDIA_URL != '/'
         and ( not settings.MEDIA_URL in prefixes ) ):
      prefixes.append( settings.MEDIA_URL )

    if ( settings.ADMIN_MEDIA_PREFIX
         and ( not settings.ADMIN_MEDIA_PREFIX in prefixes ) ):
      prefixes.append( settings.ADMIN_MEDIA_PREFIX )

    prefixes.append( '!!!initialized!!!' )
    settings.TRACKING_EXCLUDE_PREFIXES = prefixes
