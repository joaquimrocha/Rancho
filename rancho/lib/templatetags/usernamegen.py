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
from django.utils.safestring import mark_safe

register = template.Library()

def usernamegen(user, format = 'right'):
    """
    Formats a user name for show purposes.
    """

    username = user.username
    first_name = user.first_name
    last_name = user.last_name

    #we can only respect format if we have first_name and last_name
    if first_name and last_name:
        if len(username+first_name+last_name)+3>40:
            if len(last_name)>30:
                last_name = last_name[0]+'.'
            first_name = first_name[0]+'.'

        if format == 'right':
            name = "%s %s (%s) " % (first_name, last_name, username)
        elif format == 'top':
            name = "<p><strong>%s</strong></p><p><strong>%s %s</strong></p>" % (username, first_name, last_name)
        elif format == 'username':
            name = username
        elif format == 'fullname':
            name = "%s %s"%(first_name, last_name)
    else:
        if format == 'top':
            name = "<p><strong>%s</strong></p><p><strong><br/></strong></p>" % (username)
        else:
            name = username

    return mark_safe(name)

register.simple_tag(usernamegen)
