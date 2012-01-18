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

urlpatterns = patterns('rancho.file.views',
    url(r'^$','list'),
    url(r'^filter/(?P<tag>[\w\s]+)/$','list', name='file_list_tag'),

    (r'^(?P<file_id>\d+)/$', 'view_file'),

    (r'^create/$','create'),
    (r'^edit/(?P<v_id>\d+)/','edit'),
    (r'^delete/(?P<v_id>\d+)/','delete'),

    (r'^new_upload/(?P<f_id>\d+)/','new_upload'),

    (r'^send_file/(?P<v_id>\d+)/','send_file'),
)
