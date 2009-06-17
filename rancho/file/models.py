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
from rancho.tagging.fields import TagField
from rancho.company.models import Company
from rancho import djangosearch
from rancho import settings
import datetime

class FileManager(models.Manager):

    def search(self, user, query, project = None):
        files = FileVersion.index.search(query)
        if not user.is_superuser: #restrict to projects with perm
            perm = user.get_rows_with_permission(Project, PERMISSIONS_FILE_VIEW)
            project_ids = perm.values_list('object_id', flat=True)
            files = files.filter(file__project__in=project_ids)
        if project: #restrict to given project
            files = files.filter(file__project=project)
        return files

class File(models.Model):
    creator = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    
    title = models.CharField(max_length=50)    
    last_file_version = models.ForeignKey('FileVersion', related_name='lastversion', null=True)    
    notify_to = models.ManyToManyField(User, null=True, related_name='file_notify_to')
    tags = TagField()
        
    index = djangosearch.ModelIndex(text=['title'])
    
    objects = FileManager()
    
    @models.permalink
    def get_absolute_url(self):
        return ('rancho.file.views.view_file', [], {'p_id': self.project.id, 'file_id':self.id})
    

    
class FileVersion(models.Model):
    
    file = models.ForeignKey(File)
    file_location = models.FileField(upload_to=settings.UPLOAD_DIR)
    file_size= models.CharField(max_length=30)
    creation_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=500, null=True)
    creator = models.ForeignKey(User, related_name='uploader')    
    file_type= models.CharField(max_length=50)
        
    index = djangosearch.ModelIndex(text=['description'])
    
    def get_version_number(self): 
        versions = FileVersion.objects.filter(file = self.file).order_by('creation_date').values_list('id', flat = True)
        return list(versions).index(self.id)

