########################################################################
# Rancho - Open Source Group/Project Management Tool
#    Copyright (C) 2008 The Rancho Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
########################################################################

from django.http import HttpResponseForbidden
from django.template import RequestContext, loader
from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.contrib.auth.models import SiteProfileNotAvailable

from rancho.user.models import UserProfile


#Code from django-cas: http://code.google.com/p/django-cas/
def forbidden(request, template_name='403.html'):
    """Default 403 handler"""

    t = loader.get_template(template_name)
    return HttpResponseForbidden(t.render(RequestContext(request)))

class Custom403Middleware(object):
    """Catches 403 responses and renders 403.html"""

    def process_response(self, request, response):

        if isinstance(response, HttpResponseForbidden):
            return forbidden(request)
        else:
            return response

#from pinax project        
class LocaleMiddleware(object):
    """
    This is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context depending on the user's profile. This allows pages
    to be dynamically translated to the language the user desires
    (if the language is available, of course). 
    """

    def get_language_for_user(self, request):
        if request.user.is_authenticated():
            try:
                profile = request.user.get_profile()
                return profile.language
            except (SiteProfileNotAvailable, UserProfile.DoesNotExist):
                pass
        return translation.get_language_from_request(request)

    def process_request(self, request):
        translation.activate(self.get_language_for_user(request))
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept-Language',))
        response['Content-Language'] = translation.get_language()                
        translation.deactivate()
        return response
        
