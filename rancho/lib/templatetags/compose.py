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

from django.conf import settings
from django.utils.translation import ugettext as _

from django.company.models import Company

class LogoNode(template.Node):
    
    def __init__(self, logo_path='/company/logo.png'):
        self.logo_path = logo_path

    def render(self, context):
        
        return '<img src="/media'+self.logo_path+'" />'


def do_logo(parser, token):
    logo_path = token.split_contents()
    return LogoNode(logo_path[1:])

# Usage example:
# {% menu root venue_menu new_visit %}
# will render the 'root' menu with the 'venue_menu' item, if it exists, as
# active; then the 'venue_menu_ menu with the 'new_visit' item, if it
# exists, as active.

register.tag('logo', do_logo)
