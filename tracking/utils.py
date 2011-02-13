from tracking import settings
import re
import unicodedata


# this is not intended to be an all-knowing IP address regex
IP_RE = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

def get_ip(request):
    """
    Retrieves the remote IP address from the request data.  If the user is
    behind a proxy, they may have a comma-separated list of IP addresses, so
    we need to account for that.  In such a case, only the first IP in the
    list will be retrieved.  Also, some hosts that use a proxy will put the
    REMOTE_ADDR into HTTP_X_REAL_IP (for exemple nginx transparent proxy for django site)
    or into HTTP_X_FORWARDED_FOR.  This will handle pulling back the
    IP from the proper place.
    RPC allow proxy to add prosy-ip to list of remotes addreses. We handle it trying to split
    comma separated addresses and get fist good.
    """

    # if neither header contain a value, just use local loopback
    ip_address = request.META.get( 'HTTP_X_REAL_IP' ,
                                  request.META.get( 'HTTP_X_FORWARDED_FOR' ,
                                  request.META.get( 'REMOTE_ADDR', '127.0.0.1' ) ) )

    if ip_address:
        # make sure we have one and only one IP
        for addr in re.split(',\s+', ip_address ):
          m = IP_RE.match( addr )
          try:
            if m:
              return m.group( 0 );
          except IndexError:
            pass

    return '10.0.0.1'

def get_timeout():
    """
    Gets any specified timeout from the settings file, or use 10 minutes by
    default
    """
    return settings.TIMEOUT

def get_cleanup_timeout():
    """
    Gets any specified visitor clean-up timeout from the settings file, or
    use 24 hours by default
    """
    return settings.CLEANUP_TIMEOUT

def u_clean(s):
    """A strange attempt at cleaning up unicode"""
    uni = ''
    try:
        # try this first
        uni = str(s).decode('iso-8859-1')
    except UnicodeDecodeError:
        try:
            # try utf-8 next
            uni = str(s).decode('utf-8')
        except UnicodeDecodeError:
            # last resort method... one character at a time (ugh)
            if s and type(s) in (str, unicode):
                for c in s:
                    try:
                        uni += unicodedata.normalize('NFKC', unicode(c))
                    except UnicodeDecodeError:
                        uni += '-'

    return uni.encode('ascii', 'xmlcharrefreplace')

def user_agent_is_untracked(user_agent):
  import logging
  log = logging.getLogger('tracking.middleware')
  from tracking.models import UntrackedUserAgent
  from django.core.cache import cache
  
  # retrieve untracked user agents from cache
  ua_key = '_tracking_untracked_uas'
  untracked = cache.get(ua_key)
  if untracked is None:
    log.info('Updating untracked user agent cache')
    untracked = UntrackedUserAgent.objects.all()
    cache.set(ua_key, untracked, 3600)

  # see if the user agent is not supposed to be tracked
  for ua in untracked:
    # if the keyword is found in the user agent, stop tracking
    if unicode(user_agent, errors='ignore').find(ua.keyword) != -1:
      return True
  return False;

 