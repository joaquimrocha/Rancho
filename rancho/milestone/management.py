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
from rancho.milestone import models as milestone_app
    
def create_notice_types(app, created_models, verbosity, **kwargs):
    notification.create_notice_type("milestone_new", _("New milestone"), _("A new milestone has been created"))
    notification.create_notice_type("milestone_complete", _("Milestone complete"), _("A milestone has been completed"))
    notification.create_notice_type("milestone_datewarning", _("Milestone completion date approaching"), _("A milestone completion date is approaching "))
    notification.create_notice_type("milestone_updated", _("Milestone updated"), _("A milestone has been updated"))

signals.post_syncdb.connect(create_notice_types, milestone_app)    
