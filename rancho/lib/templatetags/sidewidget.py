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

def sidewidget(name, icon = ''):
    """
    Creates a right content widget.
    """
    image = ''
    if icon:
        image = '<img class="textcenter" src="/media/basepage/images/icons/%s.png" alt="" />' % icon
    widget = """
<div class="widget">
    <p>%s %s</p>
</div>
""" % (image, name)
    return mark_safe(widget)

register.simple_tag(sidewidget)
