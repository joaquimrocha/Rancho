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

urlpatterns = patterns('rancho.search.views',
    url(r'^$','search', name='search_search_general'),
    url(r'^(?P<p_id>\d+)/$','search', name='search_search_project'),
#    url(r'^filter/(?P<tag>\w+)/$','list', name='message_list_tag'),
#    (r'^create/$','create'),
#    (r'^edit/(?P<m_id>\d+)/','edit'),
#    (r'^delete/(?P<m_id>\d+)/','delete'),
#
#    (r'^read/(?P<m_id>\d+)/','read_add_comment'),
)
