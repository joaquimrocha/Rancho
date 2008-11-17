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

from django import forms
from django.utils.translation import ugettext_lazy as _

from rancho.tagging.forms import TagField
from rancho.lib.custom_widgets import AjaxTags, ShowAndSelectMultipleNotification
from rancho.file.models import File, FileVersion
from rancho.company.models import Company


class FileVersionForm(forms.Form):
    description =  forms.CharField(label=_('Description'), widget=forms.TextInput(attrs={'class':'fillx'}), max_length=500, required=False)
    tags=TagField(required=False)    
    
    def __init__(self,tagslist, request_post=None,request_file=None, *args, **kwargs):
        super(FileVersionForm, self).__init__(request_post,request_file,*args, **kwargs)
        self.fields['tags'].widget=AjaxTags(tagslist, attrs={'class':'fillx'})
        
    def save(self, file_version):
        file_version.description=self.cleaned_data['description']                                                            
        file_version.save()
        file_version.file.tags = self.cleaned_data['tags']
        file_version.file.save()


class UploadFileForm(FileVersionForm):
    file=forms.FileField(label=_('File'), widget=forms.FileInput(attrs={'class':'fillx'}),error_messages={'required': 'Please insert a file'})
    
    def __init__(self,tagslist, request_post=None,request_file=None, *args, **kwargs):
        super(UploadFileForm, self).__init__(tagslist, request_post,request_file,*args, **kwargs)
        
    def save(self, user, file):
        return _save_file_version(file, user, self.cleaned_data['file'], self.cleaned_data['tags'], self.cleaned_data['description'])        

class NewFileForm(UploadFileForm):
    title = forms.CharField(label=_('Title'),widget=forms.TextInput(attrs={'class':'fillx'}), max_length=50)    
    notify=forms.MultipleChoiceField(label=_('Notify'))
    
       
    def __init__(self,list_users, tagslist, request_post=None,request_file=None, *args, **kwargs):
        super(NewFileForm, self).__init__(tagslist, request_post,request_file,*args, **kwargs)
        
        list = [(user.id, user) for user in list_users]        
        self.fields['notify']=forms.MultipleChoiceField(widget=ShowAndSelectMultipleNotification,required=False, choices=list)
        
    def save(self, user, project):
        file=File()
        file.title=self.cleaned_data['title']
        file.creator=user
        file.project=project
        file.save()               
        _save_file_version(file, user, self.cleaned_data['file'], self.cleaned_data['tags'], self.cleaned_data['description'])
        
        [file.notify_to.add(user) for user in self.cleaned_data['notify']]
        return file
      
# helper functions
####################################################################################


def _save_file_version(file, user, realfile, tags, description):             
    file_version=FileVersion()
    file_version.file        = file
    file_version.description = description
    file_version.creator     = user
    file_version.file_size   = realfile.size
    file_version.file_type   = realfile.content_type
    file_version.save()
                    
    file_version.file_location.save(str(file.id)+'_'+str(file_version.id)+'_'+realfile.name,realfile)
    
    file.tags  = tags             
    file.last_file_version   = file_version
    file.save()
    
    return file_version

        
