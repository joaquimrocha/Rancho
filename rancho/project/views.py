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

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core import urlresolvers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from rancho.granular_permissions import permissions
from rancho.lib import utils
from rancho.lib.templatetags.usernamegen import usernamegen
from rancho.lib.utils import events_log
from rancho.project.forms import EditPermissionsForm, NewProjectForm, \
    AddPeopleForm, EditProjectSettingsForm
from rancho.project.models import Project, UserInProject
import datetime

@login_required
@user_passes_test(lambda u: u.is_superuser)
def new_project(request):
    user = request.user
        
    if request.method=='POST':        
        form = NewProjectForm(request.POST, request.FILES)        
        if form.is_valid():            
            project = form.save( user )   
            
            events_log(user, 'A', project.name, project)
                   
            return HttpResponseRedirect(urlresolvers.reverse('rancho.project.views.overview', args=[project.id]))                   
    else:        
        form = NewProjectForm()
        
    return render_to_response('project/new_project.html', 
                            {'newProjectForm' : form},
                            context_instance=RequestContext(request))

@login_required
def overview(request, p_id):    

    user = request.user
    project = get_object_or_404(Project, id=p_id)
    project.check_user_in_project_or_404(user)
    users_in_project = project.get_users()
    
    sorted_events = utils.get_overview(user, project)
    return render_to_response('project/overview.html', 
                              {'project': project, 'users_in_project': users_in_project, 'events': sorted_events, 'now': datetime.datetime.now()},
                              context_instance=RequestContext(request))
        
@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_permissions(request, p_id, user_id):
    
    project = get_object_or_404(Project, id=p_id)
    edit_user = get_object_or_404(User, id=user_id)
    project.check_user_in_project_or_404(edit_user)
    
    #dont' edit permissions of admin
    if edit_user.is_superuser:
        return HttpResponseRedirect(urlresolvers.reverse('rancho.project.views.show_people_project', args=[project.id]))
    
    if request.method=='POST':            
        form = EditPermissionsForm(request.POST)
        if form.is_valid():     
                   
            form.save(edit_user, project)
            request.user.message_set.create(message=_("Permissions updated"))            
            
            return HttpResponseRedirect(urlresolvers.reverse('rancho.project.views.show_people_project', args=[project.id]))            
    else:
        perm = permissions.get_permission_dictionary(edit_user, project)        
        form = EditPermissionsForm({'permissions': perm})
        

    
    return render_to_response('project/edit_permissions.html', 
                              {'edit_user': edit_user,
                               'project': project, 
                               'form': form,                               
                               },
                              context_instance=RequestContext(request))
    

@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_people_to_project(request, p_id):

    project = get_object_or_404(Project, id = p_id)

    if request.method=='POST':            
        form = AddPeopleForm(project.get_users_not_in(), request.POST)
        if form.is_valid():     
                   
            form.save(project)
            request.user.message_set.create(message=_("Users added to project."))            
            
            return HttpResponseRedirect(urlresolvers.reverse('rancho.project.views.show_people_project', args=[project.id]))            
    else:
        form = AddPeopleForm(project.get_users_not_in())
                     
    return render_to_response('project/addusers.html', {'form':form, 'project': project },
                                  context_instance=RequestContext(request))
     
@login_required
@user_passes_test(lambda u: u.is_superuser)
def remove_user(request, p_id):
    
    project = get_object_or_404(Project, id = p_id)
    
    if request.method == 'GET':
        user = get_object_or_404(User, id = int(request.GET.get('userid')))
        if (not user.get_profile().is_account_owner) and (not user.is_superuser):
            UserInProject.objects.filter(user=user, project=project).delete()
            user.clean_permissions(project)        
            request.user.message_set.create(message=_("User %s has been remove from project."%usernamegen(user) ))
        
    return HttpResponseRedirect(urlresolvers.reverse('rancho.project.views.show_people_project', args=[project.id]))
        
    
@login_required
def show_people_project(request, p_id):

    project = get_object_or_404(Project, id = p_id)
    users_in_project = project.get_users()

    #have company to be able to use regroup in view    
    users = []
    for user in users_in_project:
        setattr(user, 'company', user.get_profile().company)   
        users.append(user)

    return render_to_response('project/showpeople.html', 
                              {'project': project, 
                               'users_in_project': users,
                               },
                              context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_superuser)
def settings(request, p_id):
    
    project = get_object_or_404(Project, id = p_id)
    users_in_project = project.get_users()
    
    
    
    if request.method=='POST':
        form = EditProjectSettingsForm(project, request.POST, request.FILES)
        if form.is_valid():
            form.save(project)            
            request.user.message_set.create(message=_("Project settings have been successfully edited."))
            
    else:
        data = {'project_name':project.name, 
                'description':project.description, 
                'status': project.status}
        form = EditProjectSettingsForm(project, data)
    
    context = {'project': project,    
                'edit_project': form,
                'users_in_project': users_in_project}
    return render_to_response('project/settings.html', context,
                              context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_logo(request, p_id):

    project = get_object_or_404(Project, id = p_id)
    
    if project.logo:
        project.logo.delete(save=False)
        project.logo = None
        
        project.save()
    return HttpResponse("")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_project(request, p_id):
    user = request.user
    
    project = get_object_or_404(Project, id = p_id)
    events_log(user, 'D', project.name, project) 
    request.user.message_set.create(message=_("Project %s Deleted."%project.name))    
    project.delete()   
    
    
    return HttpResponseRedirect(urlresolvers.reverse('rancho.user.views.dashboard'))
