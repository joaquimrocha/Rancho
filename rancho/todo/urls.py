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

urlpatterns = patterns('rancho.todo.views',
    (r'^$', 'list'),
    (r'^(?P<todo_list_id>\d+)/$', 'view_todo_list'),
    (r'^create/$', 'create'),
    (r'^(?P<todo_list>\d+)/add/$', 'add_todo'),
    (r'^(?P<todo_list_id>\d+)/edit$', 'edit_todo_list'),
    (r'^(?P<todo_id>\d+)/edit_todo/$', 'edit_todo'),
    (r'^save_todo_changes/$', 'save_changes'),
    (r'^delete_todo/$', 'delete_todo'),
    (r'^delete_list/$', 'delete_todo_list'),
    (r'^switch_todo_status/$', 'switch_todo_status'),
)
