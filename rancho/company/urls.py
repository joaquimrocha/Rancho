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

urlpatterns = patterns('rancho.company.views',
    (r'^create/$','create_company'),
    url(r'^settings/$', 'company_settings', name='company_settings_main'),
    url(r'^edit/(?P<c_id>\d+)/$', 'edit_company', name='company_settings_def'),
    url(r'^export/$', 'export_account', name='export_account'),
    url(r'^import/$', 'import_account', name='import_account'),
    (r'^delete/$', 'delete_company'),
    (r'^delete_logo/$', 'delete_logo'),
    
    (r'^show_logs/$', 'show_logs'),
)
