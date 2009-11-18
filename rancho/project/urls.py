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

from django.conf.urls.defaults import *

urlpatterns = patterns('rancho.project.views',
    (r'^new/$', 'new_project'),
    (r'^(?P<p_id>\d+)/$', 'overview'),
    (r'^(?P<p_id>\d+)/overview/$', 'overview'),
    (r'^(?P<p_id>\d+)/settings/$', 'settings'),
    (r'^(?P<p_id>\d+)/delete_logo/$', 'delete_logo'),    
    (r'^(?P<p_id>\d+)/message/', include('rancho.message.urls')),
    (r'^(?P<p_id>\d+)/chat/', include('rancho.chat.urls')),
    (r'^(?P<p_id>\d+)/wikiboards/', include('rancho.wikiboard.urls')),
    (r'^(?P<p_id>\d+)/todos/', include('rancho.todo.urls')),
    (r'^(?P<p_id>\d+)/people/(?P<user_id>\d+)/permissions$', 'edit_permissions'),
    (r'^(?P<p_id>\d+)/people/$', 'show_people_project'),
    (r'^(?P<p_id>\d+)/people/add/', 'add_people_to_project'),
    (r'^(?P<p_id>\d+)/people/remove/', 'remove_user'),
    (r'^(?P<p_id>\d+)/milestones/', include('rancho.milestone.urls')),
    (r'^(?P<p_id>\d+)/files/', include('rancho.file.urls')),
    (r'^(?P<p_id>\d+)/delete/', 'delete_project'),
)
