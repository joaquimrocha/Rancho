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

from django.utils.translation import ugettext_lazy as _ 
from granular_permissions.permissions import PERMISSIONS_FILE_VIEW, PERMISSIONS_WIKIBOARD_VIEW, PERMISSIONS_MILESTONE_VIEW, PERMISSIONS_TODO_VIEW, PERMISSIONS_MESSAGE_VIEW, IS_ADMIN
from django.template import Variable
from granular_permissions import permissions

register = template.Library()


MENUS = {'root': (#caption, url, id, perm
                  (_('Dashboard'), '/dashboard', 'dashboard', None),
                  (_('Milestones'), '/milestones', 'milestones', None),
                  (_('Statistics'), '/statistics', 'statistics', None),
                  ),
        'inproject': (
                  (_('Overview'), '/project/%s/overview', 'overview', None),
                  (_('Messages'), '/project/%s/message', 'message', PERMISSIONS_MESSAGE_VIEW),
                  (_('ToDos'), '/project/%s/todos', 'todos', PERMISSIONS_TODO_VIEW),
                  (_('Milestones'), '/project/%s/milestones', 'milestones', PERMISSIONS_MILESTONE_VIEW),
                  (_('Wikiboards'), '/project/%s/wikiboards', 'wikiboards', PERMISSIONS_WIKIBOARD_VIEW),
                  (_('Files'), '/project/%s/files', 'files', PERMISSIONS_FILE_VIEW),
                  ),
        }

def genmenu(context, menu_title, active_menu, url=None, before_text=None, on_name=None):
    if not on_name:
        on_name=u'active'
            
    if url:  
        if type(url) in (int, long): #to support when user only puts a variable
            args = [url]
        else:          
            args = [Variable(arg).resolve(context) for arg in url.split(',')]
    else:
        args = []
    
    try:
        active_menu = active_menu
        if active_menu[-1]==u'/':
            active_menu = active_menu[0:-1]
        if active_menu[0]==u'/':
            active_menu = active_menu[1:]
    except IndexError:
        pass
        
    open_before_text = u''
    close_before_text = u''
    if before_text:
        open_before_text = u'<'+before_text+u'>'
        close_before_text = u'</'+before_text+u'>'
    menus = u'<ul>'
    menu = u''
    
    project = context.get('project')
    user = context.get('user')
    for label, url_final, id, perm in MENUS[str(menu_title)]:
        #check permission
        if permissions.checkperm(perm, user, project):        
            menu+=u'<li'
            
            if url_final[-1]==u'/':
                url_final = url_final[0:-1]
            if url_final[0]==u'/':
                url_final = url_final[1:]
            if active_menu!=u'':    
                if id==active_menu:
                    menu+=u' class="%s">' % on_name
                else:
                    menu+=u'>'
            else:
                menu+=u'>'                    
                
            if len(args) != 0:
                number_of_params_to_replace = url_final.count('%s')
                difference = number_of_params_to_replace - len(args)            
                if difference > 0:
                    for i in xrange(0, difference):
                        args.append(args[-1])
                for arg in args:
                    url_final = url_final.replace('%s', str(arg), 1)
            
            menu+=u'<a href="/%s">%s%s%s</a></li>'%(url_final, open_before_text,label, close_before_text)
            
    menus+=menu+u'</ul>'
                
    return {'menu': menus}
    
register.inclusion_tag("lib/genmenu.html", takes_context=True)(genmenu)



