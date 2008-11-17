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
register = template.Library()
from django.utils.translation import ugettext as _

def displaynotification(messages, type = 'green'):
    
    if not messages:
        return ''
    notification = '<div id="notification" class="%s_msg"><div style="float: left;">' % type
    for message in messages:
        notification += '<p>%s</p>' % message
    notification += '</div><div style="float: right; font-weight: normal;"> <a id="hide_notification" href="">(%s)</a> </div></div>' % _('Hide')
    notification += '''
    <script type="text/javascript">
        $("#hide_notification").click(
            function() {
                $("#notification").hide();
                return false;
            }
        );
    </script>'''
    return notification

register.simple_tag(displaynotification)
