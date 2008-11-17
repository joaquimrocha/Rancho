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
from django.http import Http404
from django.db.models import Q

from rancho.company.models import Company

from rancho import settings

class ProjectManager(models.Manager):    
    
    def get_projects_for_user(self, user, status = 'A'):
        #return [user_in_project.project for user_in_project in UserInProject.objects.filter(user = user, state = status)]
        if user.is_superuser:
            return self.filter(status=status)
        else:
            return user.project_set.filter(status=status)

class Project(models.Model):
    
    PROJECT_STATUS_CHOICES = (('A', 'Active'), ('Z','Frozen'), ('F','Finished'),)
    
    name = models.CharField(max_length=50)
    creation_date = models.DateTimeField(auto_now_add=True)
    finish_date = models.DateTimeField(null=True)
    
    logo = models.ImageField(upload_to=settings.PROJECT_DIR, blank=True, null=True)
    status = models.CharField(max_length=1, choices=PROJECT_STATUS_CHOICES)
    
    creator = models.ForeignKey(User, related_name='creator')    
    description = models.CharField(max_length=500, null=True)
        
    users = models.ManyToManyField(User, through='UserInProject')
    objects = ProjectManager()
    company = models.ForeignKey(Company)
        
    def get_users(self, status = 'a'):
        #LR: distinct should be necessary... think about a better query        
        return (User.objects.filter(is_superuser=True, is_active=True) |  User.objects.filter(is_active=True, project=self, userinproject__state='a' )).distinct().order_by('userprofile__company')

    
    def get_users_not_in(self):
        return User.objects.filter(is_active=True).exclude(project=self).exclude(is_superuser=True, is_active=True).order_by('userprofile__company')
        
    def check_user_in_project_or_404(self, user):
        if  (not self.users.filter(userinproject__user=user)) and (not user.is_superuser) :
            raise Http404('No %s matches the given query.'%self._meta.object_name)    
    
    
    def __unicode__(self):
        return 'Project: id-' + str(self.id) + ' name-' +self.name
    
class UserInProject(models.Model):    
    STATE_CHOICES = (('a','Active'), ('r', 'Removed'), ('m', 'Readmited'),)
        
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    added_date = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=1,choices=STATE_CHOICES)
    
    
