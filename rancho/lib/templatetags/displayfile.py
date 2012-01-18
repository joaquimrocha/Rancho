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
from datetime import date
register = template.Library()
import settings
import os.path

def displayfile(context, file_and_versions, user):
    file_object, versions = file_and_versions
    last_version = versions[0]
    del versions[0]

    is_image = False
    if last_version[2].file_type.split('/')[0] == 'image':
        is_image = True
    for i in xrange(len(versions)):
        versions[i] += (__get_icon_from_file((versions[i])[2].file_location),)

    context = {'file': file_object, 'last_version': last_version[2],
               'last_version_name': last_version[1], 'last_version_number': last_version[0],
               'last_version_icon': __get_icon_from_file(last_version[2].file_location),
               'versions': versions, 'project': file_object.project,
               'user': user, 'is_image': is_image}
    return context

def __get_icon_from_file(file):
    ext = os.path.splitext(file.name)[1].strip('.')
    if ext:
        if os.path.exists(settings.MEDIA_ROOT + '/icons/16/' + ext + '.png') and \
            os.path.exists(settings.MEDIA_ROOT + '/icons/32/' + ext + '.png'):
            return ext + '.png'
    return 'other.png'

register.inclusion_tag("lib/displayfile.html", takes_context=True)(displayfile)
