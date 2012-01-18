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

from granular_permissions import permissions

class ComparisonNode(template.Node):

    def __init__(self, permission, user, project, object, nodelist_true, nodelist_false):
        self.permission = permission.strip('"')
        self.user = user
        self.object = object
        self.project = project
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false

    def render(self, context):
        try:
            user = template.Variable(self.user).resolve(context)
            if self.object:
                object = template.Variable(self.object).resolve(context)
            else:
                object = None
            if self.project:
                project = template.Variable(self.project).resolve(context)
            else:
                project = None

            permission = eval('permissions.%s'%self.permission)

            if permissions.checkperm(permission, user, project, object):
                return self.nodelist_true.render(context)
        # If either variable fails to resolve, return nothing.
        except template.VariableDoesNotExist:
            return ''
        # If the types don't permit comparison, return nothing.
        except TypeError:
            return ''
        return self.nodelist_false.render(context)


def do_if_has_perm(parser, token):
    """

    """
    bits = token.contents.split()
    if 5 < len(bits) < 4:
        raise template.TemplateSyntaxError("'%s' tag takes four or five arguments" % bits[0])
    end_tag = 'endifhasperm'
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    if len(bits) == 5:
        obj = bits[4]
    else:
        obj = None
    return ComparisonNode(bits[1], bits[2], bits[3], obj , nodelist_true, nodelist_false)

register.tag('ifhasperm', do_if_has_perm)


