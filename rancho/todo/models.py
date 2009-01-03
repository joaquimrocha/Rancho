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

import datetime

class ToDoList(models.Model):        
    creator = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    
    responsible = models.ForeignKey(User, related_name='todolistresponsible', null=True)
    
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500, null=True)
    
    number_of_todos = models.IntegerField(default=0)
        
    def get_todos(self):
        return ToDo.objects.filter(todo_list = self)

class ToDo(models.Model):
    
    creator = models.ForeignKey(User, related_name='todocreator')
    responsible = models.ForeignKey(User, related_name='todoresponsible', null=True)

    todo_list = models.ForeignKey(ToDoList)
    description = models.CharField(max_length=500)
    completion_date = models.DateTimeField(null=True)
    creation_date = models.DateTimeField(default = datetime.datetime.now())
    position = models.IntegerField(default = 0)        