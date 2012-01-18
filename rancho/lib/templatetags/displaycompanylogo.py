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
import os
import settings

register = template.Library()

def displaycompanylogo(company):
    """
    Displays project logo if the image exists or its name
    """

    if company.logo and os.path.exists(os.path.join(settings.MEDIA_URL, company.logo.path)) and company.display_logo_name:
        return mark_safe('<img src="/media/%s" alt="%s"/>' % (company.logo, company.short_name))
    else:
        return mark_safe('<p style="margin-right: 20px;">%s</p>' % company.short_name)

register.simple_tag(displaycompanylogo)
