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

def displaytodo(context, todo, user = None):
    image = 'notcheck.png'
    if todo.completion_date:
        image = 'check.png'
    project = todo.todo_list.project
    result = {'todo': todo, 'image': image, 'project': project, 'user': user}
    return result

register.inclusion_tag("lib/displaytodo.html", takes_context=True)(displaytodo)
