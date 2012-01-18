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

from django import template
from lib.templatetags.usernamegen import usernamegen
import settings
register = template.Library()
from django.utils.translation import ugettext as _

def displayuserphoto(context, user, size = ''):
    """
    Displays user's photo if any.
    """
    user_profile = user.get_profile()
    if user_profile != None:

        username = usernamegen(user, 'fullname')
        photo = settings.MEDIA_URL + 'general/user_nopic_small.png'
        if size == 'small' or not size:
            if user_profile.small_photo:
                photo = settings.MEDIA_URL + str(user_profile.small_photo)
        elif size == 'large':
            if user_profile.large_photo:
                photo = settings.MEDIA_URL + str(user_profile.large_photo)
        return {
                'photo': photo,
                'title': _("%s's Photo" % username)
                }

register.inclusion_tag("lib/displayuserphoto.html", takes_context=True)(displayuserphoto)
