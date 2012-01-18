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
def displaystatistic(context, name, trans_name, number):
    icons_folder = '/media/basepage/images/icons/'
    icon = ''
    if name == 'message':
        icon = 'comment.png'
    elif name == 'milestone':
        icon = 'clock.png'
    elif name == 'wikiboard':
        icon = 'page.png'
    elif name == 'file':
        icon = 'page_white_put.png'
    elif name == 'todo':
        icon = 'note.png'
    icon = icons_folder + icon
    return {'icon': icon, 'name': trans_name, 'number': number}

register.inclusion_tag("lib/displaystatistic.html", takes_context=True)(displaystatistic)
