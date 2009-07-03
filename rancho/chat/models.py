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
from django.db import models
from rancho.project.models import Project

class Post(models.Model):
    
    date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, null=True, blank=True)
    message = models.CharField(max_length=1000)
    project = models.ForeignKey(Project, null = True, blank = True)

class ChatData(models.Model):
    
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project, null = True, blank = True) 
    last_request = models.IntegerField()
    is_connected = models.BooleanField(default = False)
