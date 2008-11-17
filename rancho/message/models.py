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

from rancho.project.models import Project
from rancho.file.models import File
from rancho.tagging.fields import TagField
from rancho import djangosearch

class Message(models.Model):    
    creator = models.ForeignKey(User, related_name='messagecreator')
    project = models.ForeignKey(Project)

    creation_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)
    body = models.TextField()
    
    tags = TagField()
    attachment = models.ForeignKey(File, null=True)
    initial_message = models.ForeignKey('self', null=True)
    
    notify_to = models.ManyToManyField(User,null=True, related_name='message_notify_to')
    read_by = models.ManyToManyField(User,null=True, related_name='message_read_by')
    
    index = djangosearch.ModelIndex(text=['title', 'body'])
        
    
    def __unicode__(self):
        return 'Subject: '+self.title + ' creator: '+self.creator.first_name + ' '+ self.creator.last_name
