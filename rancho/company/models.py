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

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from rancho import settings


class Company(models.Model):
    short_name = models.CharField(max_length=100)
    long_name = models.CharField(max_length=200)

    description = models.CharField(max_length=500, null=True)

    phone = models.CharField(max_length=20, null=True)
    mailing_address = models.TextField(max_length=500, null=True)
    webpage = models.URLField(max_length = 500, null=True)

    logo = models.ImageField(upload_to = settings.COMPANY_DIR, null=True)
    display_logo_name = models.BooleanField(default=False)

    language = models.CharField(max_length=5, choices=settings.LANGUAGES)

    main_company = models.BooleanField(default=False)

class EventsHistory(models.Model):
    EVENT_TYPE = (#general
                  ('D', _('Delete')), ('A', _('Add')), ('U', _('Update')),
                  #milestone and todo based
                  ('ICOMP', _('Set as Incomplete')), ('COMP', _('Set as Complete')),
                  )

    user = models.ForeignKey(User, related_name='huser')
    date = models.DateTimeField(auto_now =True)
    type = models.CharField(max_length=5, choices=EVENT_TYPE)
    title = models.CharField(max_length=200)


    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
