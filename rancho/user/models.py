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

from django.db import models
from django.contrib.auth.models import User

from rancho.timezones.forms import TIMEZONE_CHOICES
from rancho import  settings
from rancho.timezones.fields import TimeZoneField

class UserProfile(models.Model):
    YES_NO_CHOICES = (('1', 'Yes'), ('0', 'No'),)
    
    IM_SERVICES_CHOICES = ( ('A', 'AOL'), ('G', 'Google'), ('I', 'ICQ'), 
                            ('J', 'Jabber'), ('S', 'Skype'), ('Y', 'Yahoo'), 
                            ('M', 'MSN'),
                            )
    
    user = models.ForeignKey(User, unique=True)
    
    title = models.CharField(max_length=15, null=True)
    
    company = models.ForeignKey('company.Company', null=True)

    office = models.CharField(max_length=50, null=True)
    office_phone = models.CharField(max_length=20, null=True)
    office_phone_ext = models.CharField(max_length=5, null=True)
    mobile_phone = models.CharField(max_length=20, null=True)
    home_phone = models.CharField(max_length=20, null=True)
    
    im_name = models.CharField(max_length=100, null=True)
    im_service = models.CharField(max_length=1, choices=IM_SERVICES_CHOICES, null=True)
    
    small_photo = models.ImageField(upload_to=settings.PEOPLE_DIR, blank=True, null=True)
    large_photo = models.ImageField(upload_to=settings.PEOPLE_DIR, blank=True, null=True)
    
    mailing_address = models.TextField(null=True)
    
    webpage = models.URLField(null=True)    
    
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    timezone = TimeZoneField()
    
    is_account_owner = models.BooleanField(default=False)
    
    def __unicode__(self):
        return str(self.user.username)
    
