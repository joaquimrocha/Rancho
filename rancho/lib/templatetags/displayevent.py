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
from django.utils.translation import ugettext as _
from message.models import Message
from milestone.models import Milestone
from lib import utils

register = template.Library()
def displayevent(context, event):
    name, icon, description, user_info, action, complete, url = utils.get_object_overview_info(event)
    return {'event': event, 'name': name, 'icon': icon, 'description': description, 'user_info': user_info, 'action': action, 'complete': complete, 'url': url}

register.inclusion_tag("lib/displayevent.html", takes_context=True)(displayevent)

def displayeventlog(context, event):
    return {'event': event, 'user': context['user']}

register.inclusion_tag("lib/displayeventlog.html", takes_context=True)(displayeventlog)
