from datetime import datetime, timedelta
import logging
import re
import traceback

from tracking.settings import NO_TRACKING_PREFIXES
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.db.utils import DatabaseError
from django.http import Http404
from tracking import utils
from tracking.models import Visitor, BannedIP, UntrackedUserAgent

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

title_re = re.compile('<title>(.*?)</title>')
log = logging.getLogger('tracking.middleware')

class VisitorTrackingMiddleware:
    """
    Keeps track of your active users.  Anytime a visitor accesses a valid URL,
    their unique record will be updated with the page they're on and the last
    time they requested a page.

    Records are considered to be unique when the session key and IP address
    are unique together.  Sometimes the same user used to have two different
    records, so I added a check to see if the session key had changed for the
    same IP and user agent in the last 5 minutes
    """

    def process_request(self, request):
        # don't process AJAX requests
        if request.is_ajax(): return

        # create some useful variables
        ip_address = utils.get_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

	if utils.user_agent_is_untracked( user_agent ):
          log.debug('Not tracking UA "%s" because of keyword: %s' % (user_agent, ua.keyword))
          return

        if hasattr(request, 'session'):
            # use the current session key if we can
            session_key = request.session.session_key
        else:
            # otherwise just fake a session key
            session_key = md5( '%s:%s' % ( ip_address, user_agent ) ).hexdigest()

        # ensure that the request.path does not begin with any of the prefixes
        for prefix in NO_TRACKING_PREFIXES:
            if request.path.startswith(prefix):
                log.debug('Not tracking request to: %s' % request.path)
                return

        # if we get here, the URL needs to be tracked
        # determine what time it is
        now = datetime.now()

        attrs = {
            'session_key': session_key,
            'ip_address': ip_address
        }

        # for some reason, Visitor.objects.get_or_create was not working here
        try:
            visitor = Visitor.objects.get(**attrs)
        except Visitor.DoesNotExist:
            # see if there's a visitor with the same IP and user agent
            # within the last 5 minutes
            cutoff = now - timedelta(minutes=5)
            visitors = Visitor.objects.filter(
                ip_address=ip_address,
                user_agent=user_agent[:255],
                last_update__gte=cutoff
            )

            if len(visitors):
                visitor = visitors[0]
                visitor.session_key = session_key
                log.debug('Using existing visitor for IP %s / UA %s: %s' % (ip_address, user_agent, visitor.id))
            else:
                # it's probably safe to assume that the visitor is brand new
                visitor = Visitor(**attrs)
                log.debug('Created a new visitor: %s' % attrs)
        except:
            return

        # determine whether or not the user is logged in
        user = request.user
        if isinstance(user, AnonymousUser):
            user = None

        # update the tracking information
        visitor.user = user
        visitor.user_agent = user_agent[:255]

        # if the visitor record is new, or the visitor hasn't been here for
        # at least an hour, update their referrer URL
        if not visitor.last_update or visitor.last_update <= ( now - timedelta( hours = 1 ) ) :
            visitor.referrer = utils.u_clean(request.META.get('HTTP_REFERER', 'unknown')[:255])

            # reset the number of pages they've been to
            visitor.page_views = 0
            visitor.session_start = now

        visitor.url = request.path[:255]
        visitor.page_views += 1
        visitor.last_update = now
        visitor.save()

class VisitorCleanUpMiddleware:
    """Clean up old visitor tracking records in the database"""

    def process_request(self, request):
        timeout = utils.get_cleanup_timeout()

        if str(timeout).isdigit():
            log.debug('Cleaning up visitors older than %s hours' % timeout)
            timeout = datetime.now() - timedelta(hours=int(timeout))
            try:
              Visitor.objects.filter(last_update__lte=timeout).delete()
            except:
              pass

class BannedIPMiddleware:
    def process_request(self, request):
        key = '_tracking_banned_ips'
        ips = cache.get(key)
        if ips is None:
            # compile a list of all banned IP addresses
            log.info('Updating banned IPs cache')
            ips = [b.ip_address for b in BannedIP.objects.all()]
            cache.set(key, ips, 3600)

        # check to see if the current user's IP address is in that list
        if utils.get_ip(request) in ips:
            raise Http404
