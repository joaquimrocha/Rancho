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
import datetime

def displaychatline(chat_object, log = False):
    if not chat_object:
        return ''
    css_class = ''
    if log == "True":
        css_class = ' class="gray" '
    time = chat_object.date.strftime('%H:%M:%S')
    content = '''{%% load humanize %%}
    <p style="padding: 2px 0 2px 0;" %(css_class)s>({{ date|naturalday }} %(time)s) <strong>%(author)s</strong>: {{ message|linebreaksbr }}</p>''' % {
                                                                            'author': chat_object.author,
                                                                            'time': time,
                                                                            'css_class': css_class}
    content = template.loader.get_template_from_string(content).render(template.Context({'date': chat_object.date,
                                                                                         'message': chat_object.message}))
    return content

register.simple_tag(displaychatline)
