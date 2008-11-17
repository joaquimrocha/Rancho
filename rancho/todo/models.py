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


class ToDoList(models.Model):        
    creator = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    
    responsible = models.ForeignKey(User, related_name='todolistresponsible', null=True)
    
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500, null=True)
    
    number_of_todos = models.IntegerField(default=0)
        
    def get_todos(self):
        return [todo_in_todolist.todo for todo_in_todolist in ToDo_in_ToDoList.objects.filter(todolist = self)]

class ToDo(models.Model):
    
    SEND_EMAIL_CHOICES = (('1', 'Yes'), ('0', 'No'),)
    
    creator = models.ForeignKey(User, related_name='todocreator')
    responsible = models.ForeignKey(User, related_name='todoresponsible', null=True)
    
    description = models.CharField(max_length=50)
    completion_date = models.DateTimeField(null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    def get_todo_list(self):
        return ToDo_in_ToDoList.objects.get(todo = self).todolist

class ToDo_in_ToDoList(models.Model):
    
    todo = models.ForeignKey(ToDo)
    todolist = models.ForeignKey(ToDoList)
    
    position = models.CharField(max_length=3)
    
    class Meta:
        
        unique_together = (('todo', 'todolist'),)
