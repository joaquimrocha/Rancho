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

from rancho import settings

urlpatterns = patterns('django.views.generic.simple',    
    (r'^$', 'redirect_to', {'url': 'dashboard/'}),
    (r'^legal_notice/$', 'direct_to_template', {'template': 'legal_notice.html'}, 'legal_notice'),
)

urlpatterns = urlpatterns + patterns('',

    (r'^notification/', include('rancho.notification.urls')),

    (r'^dashboard/$', 'rancho.user.views.dashboard'),
    (r'^milestones/$', 'rancho.user.views.milestones'),
    (r'^statistics/$', 'rancho.user.views.statistics'),

    (r'^auth/', include('rancho.auth.urls')),    
    (r'^project/', include('rancho.project.urls')),
    (r'^company/', include('rancho.company.urls')),
    (r'^people/', include('rancho.user.urls')),
    (r'^calendar/', include('rancho.cal.urls')),
    (r'^search/', include('rancho.search.urls')),
    
    (r'^tinymce/', include('tinymce.urls')),

)

if getattr(settings, 'LOCAL_DEV', False):
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':  settings.MEDIA_ROOT}),
)
