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
from django.template.loader import render_to_string
from django.core import urlresolvers
register = template.Library()


class RequestBoxNode(template.Node):
    def __init__(self, type, title, description, nodelist):
        self.type = type.strip('"')
        self.title = template.Variable(title)
        self.description = template.Variable(description)

        self.nodelist = nodelist

    def render(self, context):
        tmpc = context
        tmpc['type'] = self.type
        tmpc['title'] = self.title.resolve(context)
        tmpc['description'] = self.description.resolve(context)

        html = render_to_string('lib/form_tags/beginrequestbox.html', tmpc)
        html += self.nodelist.render(context)
        html += render_to_string('lib/form_tags/endrequestbox.html', tmpc)

        return html

def do_requestbox(parser, token):
    """
    begins a request box
    beginrequestbox type tile description

    type can be: required | notrequired
    tile is a text, can be empty
    description is a text, can be empty
    """
    bits = token.split_contents()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes three arguments" % bits[0])

    nodelist = parser.parse('endrequestbox')
    token = parser.next_token()

    return RequestBoxNode(bits[1], bits[2], bits[3], nodelist)

register.tag('beginrequestbox', do_requestbox)


class OptionalGroupNode(template.Node):
    def __init__(self, id, visible, title, nodelist):
        self.id = id.strip('"')
        self.visible = visible.strip('"')
        self.title = template.Variable(title)
        self.nodelist = nodelist

    def render(self, context):
        mycontext = {'jsid': self.id,
                    'visible': self.visible,
                    'title':  self.title.resolve(context)}
        html = render_to_string('lib/form_tags/beginoptionalgroup.html', mycontext)
        html += self.nodelist.render(context)
        html += render_to_string('lib/form_tags/endoptionalgroup.html', mycontext)

        return html

def do_optionalgroup(parser, token):
    """
    begins a optional group (part of a request box)
    beginoptionalgroup visible

    id unique id for js
    visible can be: true | false
    title
    """
    bits = token.split_contents()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes three arguments" % bits[0])

    nodelist = parser.parse('endoptionalgroup')
    token = parser.next_token()

    return OptionalGroupNode(bits[1], bits[2], bits[3], nodelist)

register.tag('beginoptionalgroup', do_optionalgroup)


def printfield(context, field, place):
    """
    Prints a field on a given place
    field is a form field
    place can be top or side
    """
    return {'field': field, 'placement': place }
register.inclusion_tag("lib/form_tags/printfield.html", takes_context=True)(printfield)

def printformfooter(context, submitlabel, cancellabel, url):
    l = url.split(' ')
    view = l[0]
    argslist = []
    kwargslist = {}
    urln = ''
    if len(l) == 2:
        params = l[1].split(',')
        if '=' in l[1]:
            for p in params:
                key, value = p.split('=', 1)
                value = template.Variable(value).resolve(context)
                kwargslist[str(key)] = value
            urln = urlresolvers.reverse(view, kwargs = kwargslist)
        else:
            for p in params:
                argslist.append(template.Variable(p).resolve(context))
            urln = urlresolvers.reverse(view, args = argslist)
    else:
        urln = urlresolvers.reverse(view)
    return {'url': urln, 'submitlabel': submitlabel, 'cancellabel': cancellabel}
register.inclusion_tag("lib/form_tags/printformfooter.html", takes_context=True)(printformfooter)
