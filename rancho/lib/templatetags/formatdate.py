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
from timezones.utils import localtime_for_timezone
import datetime

register = template.Library()

def formatdate(user, date, display_time = None):
    """
    Formats a given date.
    """
    get_hours = False
    if isinstance(date, datetime.datetime):
        get_hours = True
        if display_time == 'False':
            get_hours = False
    tzdate = localtime_for_timezone(date, user.get_profile().timezone)
    return {'date' : tzdate, 'get_hours': get_hours}

register.inclusion_tag("lib/formatdate.html", takes_context = False)(formatdate)
