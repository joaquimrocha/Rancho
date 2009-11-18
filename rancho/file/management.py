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

from django.db.models import signals
from django.utils.translation import ugettext_noop as _

from rancho.notification import models as notification
from rancho.file import models as file_app

def create_notice_types(app, created_models, verbosity, **kwargs):
    notification.create_notice_type("file_new", _("New file"), _("A new file has been uploaded"))
    notification.create_notice_type("fileversion_new", _("New file version"), _("A new version of a file has been uploaded"))

signals.post_syncdb.connect(create_notice_types, file_app)
