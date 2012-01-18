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

urlpatterns = patterns('rancho.user.views',
            (r'^$', 'all_people'),
            (r'^new/$', 'newuser'),
            (r'^enable/$', 'enable_user'),
            (r'^disable/$', 'disable_user'),
            (r'^(?P<user_id>\d+)/edit/$', 'edituser'),
            (r'^(?P<user_id>\d+)/$', 'view_user'),
            (r'^(?P<user_id>\d+)/delete/$', 'deleteUser'),
            (r'^(?P<user_id>\d+)/delete_small_photo/$', 'delete_small_photo'),
            (r'^(?P<user_id>\d+)/delete_large_photo/$', 'delete_large_photo'),
            (r'^change_language/$', 'change_language'),

            )
