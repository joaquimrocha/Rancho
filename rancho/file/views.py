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

from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template.context import RequestContext
from django.core import urlresolvers
from django.http import Http404
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from rancho.file.forms import NewFileForm, UploadFileForm, FileVersionForm
from rancho.project.models import Project
from rancho.file.models import File, FileVersion
from rancho.granular_permissions.permissions import checkperm
from rancho.granular_permissions.permissions import PERMISSIONS_FILE_CREATE, PERMISSIONS_FILE_VIEW, PERMISSIONS_FILE_EDITDELETE
from rancho.notification import models as notification
from rancho.lib import utils
from rancho.tagging.models import TaggedItem, Tag

import os
from rancho import settings



# Basic operations for this app
####################################################################################

@login_required
def list(request,p_id, tag=None):

    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    project.check_user_in_project_or_404(user)    
    users_in_project = project.get_users()
    
    if not checkperm(PERMISSIONS_FILE_VIEW, user, project ):
        return HttpResponseForbidden(_('Forbidden Access'))

    #Get all the files (consider tag filter)
    if tag:
        tag = "\"%s\""%tag
        files = TaggedItem.objects.get_by_model(File, tag)
    else:
        files = File.objects
    files = files.filter(project=project).order_by('-id')
            
    file_list=[]            
    for file in files:
        file_version_list=[]
        versions = FileVersion.objects.filter(file = file).order_by('-creation_date')
        index=versions.count()
        for file_version in versions:
            #TODO: ROCHA: this is ugly... think about cleaning please
            file_name = str(_remove_ids_from_file(file_version.file_location))
            file_version_list.append((index, file_name, file_version))
            index -= 1
        file_list.append((file, file_version_list))
        
    file_tags = Tag.objects.cloud_for_model(File, steps=6, filters=dict(project=project))
                    
    context = {
               'project': project,
               'users_in_project': users_in_project,
               'files':file_list, 
               'file_tags': file_tags,
               'media_path': 'http://'+request.META['HTTP_HOST'] + settings.MEDIA_URL+'icons/',
               }
    return render_to_response('file/list_file.html', context,
                              context_instance = RequestContext(request))

@login_required
def view_file(request, p_id, file_id):
    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    project.check_user_in_project_or_404(user)    
    users_in_project = project.get_users()
    file = get_object_or_404(File, id = file_id)
    
    if not checkperm(PERMISSIONS_FILE_VIEW, user, project ):
        return HttpResponseForbidden(_('Forbidden Access'))
    
    file_list = []
    file_version_list=[]
    versions = FileVersion.objects.filter(file = file).order_by('-creation_date')
    index = versions.count()
    for file_version in versions:
        file_name = str(_remove_ids_from_file(file_version.file_location))
        file_version_list.append((index, file_name, file_version))
        index -= 1
    file_list.append((file, file_version_list))
    
    context = {
               'project': project,
               'users_in_project': users_in_project,
               'files': file_list,
               'media_path': 'http://'+request.META['HTTP_HOST'] + settings.MEDIA_URL+'icons/',
               'view_alone': True
                }
    return render_to_response('file/list_file.html', context,
                              context_instance = RequestContext(request))

@login_required
def create(request, p_id):

    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    project.check_user_in_project_or_404(user)    
    users_in_project = project.get_users()
    
    if not checkperm(PERMISSIONS_FILE_CREATE, user, project ):
        return HttpResponseForbidden(_('Forbidden Access'))


    tags = utils.get_site_tags(project)
    
    users_to_notify = utils.get_users_to_notify(project, PERMISSIONS_FILE_VIEW)

    if request.method == 'POST':
        form = NewFileForm(users_to_notify, tags, request.POST,request.FILES)
        if form.is_valid():
            file = form.save(user, project)   
                                     
            link_url = u"http://%s%s" % ( unicode(Site.objects.get_current()), urlresolvers.reverse('rancho.file.views.view_file', kwargs={'p_id': project.id, 'file_id':file.id}),)
            notification.send(file.notify_to.all(), "file_new", {'link_url': link_url, 'file': file, 'file_name': os.path.basename(file.last_file_version.file_location.path)}) 
            
            request.user.message_set.create(message = _('File "%s" successfully uploaded') % file.title )            
            return HttpResponseRedirect(urlresolvers.reverse('rancho.file.views.list', args=[project.id]))                
    else:
        form = NewFileForm(users_to_notify, tags)
    
    context = {'project': project,
               'users_in_project': users_in_project,
               'form': form
                }   
    return render_to_response('file/new_file.html',context,
                              context_instance=RequestContext(request))                
    


@login_required
def edit(request,p_id,v_id):

    user = request.user    
    project = get_object_or_404(Project, pk=p_id)    
    project.check_user_in_project_or_404(user)
    file_version = get_object_or_404(FileVersion, pk=v_id)
    
    users_in_project = project.get_users()
    
    if not checkperm(PERMISSIONS_FILE_EDITDELETE, user, project, file_version) or file_version.file.project != project:
        return HttpResponseForbidden(_('Forbidden Access'))
        
    tags = utils.get_site_tags(project)                              
    if request.method == 'POST':
        form=FileVersionForm(tags, request.POST)
        if form.is_valid():
            form.save( file_version )
            return HttpResponseRedirect(urlresolvers.reverse('rancho.file.views.list', args=[project.id]))
    else:
        form=FileVersionForm(tags, {'tags': file_version.file.tags, 'description': file_version.description})

    context = {'project': project,
               'users_in_project': users_in_project,
               'form':form,  
               'file_version': file_version,             
                'title': file_version.file.title,
                }

    return render_to_response('file/edit_version.html',context,
                              context_instance=RequestContext(request))
                
@login_required               
def delete(request,p_id,v_id):

    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    project.check_user_in_project_or_404(user)    
    file_version = get_object_or_404(FileVersion, pk=v_id)
        
    if not checkperm(PERMISSIONS_FILE_EDITDELETE, user, project, file_version ) or file_version.file.project != project:
        return HttpResponseForbidden(_('Forbidden Access'))
                
    #delete all versions if main or delete just one       
    if file_version.file.last_file_version == file_version:
        FileVersion.objects.filter(file=file_version.file).delete()
        File.objects.filter(id=file_version.file.id).delete()                    
    else:        
        file_version.delete()
    request.user.message_set.create(message = _('File successfully deleted'))
    return HttpResponseRedirect(urlresolvers.reverse('rancho.file.views.list', args=[project.id]))                
                

# other functions (realated to urls)
####################################################################################

@login_required
def new_upload(request,p_id,f_id):    

    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    project.check_user_in_project_or_404(user)
    file = get_object_or_404(File, pk=f_id)
    
    users_in_project = project.get_users()
    
    if not checkperm(PERMISSIONS_FILE_CREATE, user, project ) or file.project != project:
        return HttpResponseForbidden(_('Forbidden Access'))

    tags = utils.get_site_tags(project)
    
    if request.method == 'POST':
        form=UploadFileForm(tags,request.POST,request.FILES)
        if form.is_valid(): 
            form.save(user, file)
             
            link_url = u"http://%s%s" % ( unicode(Site.objects.get_current()), urlresolvers.reverse('rancho.file.views.view_file', kwargs={'p_id': project.id, 'file_id':file.id}),)
            notification.send(file.notify_to.all(), "fileversion_new", {'link_url': link_url, 'file': file, 'file_name': os.path.basename(file.last_file_version.file_location.path)})
           
            request.user.message_set.create(message=_("New file revision created"))
            return HttpResponseRedirect(urlresolvers.reverse('rancho.file.views.list', args=[project.id]))                
    else:
        form = UploadFileForm(tags)
        
    context = {'project': project,
               'users_in_project': users_in_project,
               'file': file,
               'form':form,                              
                }

    return render_to_response('file/new_upload.html',context,
                              context_instance=RequestContext(request))

@login_required 
def send_file(request, p_id, v_id): 
    
    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    project.check_user_in_project_or_404(user)
    file_version = get_object_or_404(FileVersion, pk=v_id)
            
    if not checkperm(PERMISSIONS_FILE_VIEW, user, project ) or file_version.file.project != project:
        return HttpResponseForbidden(_('Forbidden Access'))
         
    filepath = os.path.join(settings.MEDIA_ROOT,file_version.file_location.name)
    realfilename = file_version.file_location.name.split('_', 2)[-1]
    return utils.send_file(filepath, realfilename ) 

    
    
# helper functions
####################################################################################
              
def _remove_ids_from_file(file_name):
    file_name = str(file_name)
    file_name = file_name[file_name.find('_')+1:]
    file_name = file_name[file_name.find('_')+1:]
    return file_name
                
