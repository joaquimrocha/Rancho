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

urlpatterns = patterns('rancho.wikiboard.views',
    url(r'^$', 'list'),
    url(r'^create/$', 'create'),
    url(r'^edit/(?P<entry_id>\d+)/(?P<entry_version>\d+)/$', 'edit', name='wikiboard_edit_old'),
    url(r'^edit/$', 'edit', name='wikiboard_edit_new'),
    url(r'^delete/(?P<entry_id>\d+)/$','delete'),
    
    url(r'^view_page/(?P<entry_id>\d+)/(?P<entry_version>\d+)/$','view_page'),    
    url(r'^export_wiki/(?P<entry_id>\d+)/(?P<entry_version>\d+)/(?P<file_type>[^/]+)/$','export_wiki'),
)
                       
