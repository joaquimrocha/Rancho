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

from datetime import date, timedelta
from django.contrib.sites.models import Site
from django.core import urlresolvers
from rancho.granular_permissions.permissions import PERMISSIONS_MILESTONE_VIEW
from rancho.lib import utils
from rancho.milestone.models import Milestone
from rancho.notification import models as notification
 


def run_milestone_cron():
    """
    for each upcomming milestone send a menssage to its users remiding they are late
    """
    DAYS = 2       

    for milestone in Milestone.objects.filter(sent_notification=False, due_date__range=(date.today(),date.today()+timedelta(DAYS))):
        milestone.sent_notification = True
        milestone.save()
                
        if milestone.send_notification_email:
            link_url = u"http://%s%s" % ( Site.objects.get_current(), urlresolvers.reverse('rancho.milestone.views.list', args = [milestone.project.id]))            
            if milestone.responsible: #just notify one person                                
                notification.send([milestone.responsible], "milestone_datewarning", {'link_url': link_url, 'milestone': milestone })
            else: #notify all users with perm
                users_to_notify = utils.get_users_to_notify(milestone.project, PERMISSIONS_MILESTONE_VIEW)
                notification.send(users_to_notify, "milestone_datewarning", {'link_url': link_url, 'milestone': milestone })
        
