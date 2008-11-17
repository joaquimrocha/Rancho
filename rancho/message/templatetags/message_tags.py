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

def iconformessage(message, user):
    """
    """
    icons_folder = '/media/basepage/images/icons/'
    if message.read_by.filter(id = user.id):
        icon = icons_folder + 'comment_red.png'
    else:
        icon = icons_folder + 'comment.png'
    return mark_safe('<img src="%s" alt="" class="textcenter" title="To Read"/>' % icon)
    
register.simple_tag(iconformessage)
