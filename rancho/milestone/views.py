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

from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from rancho.granular_permissions.permissions import PERMISSIONS_MILESTONE_VIEW, \
    PERMISSIONS_MILESTONE_CREATE, PERMISSIONS_MILESTONE_EDITDELETE, checkperm
from rancho.lib import utils
from rancho.lib.utils import events_log
from rancho.milestone.forms import NewMilestoneForm
from rancho.milestone.models import Milestone
from rancho.notification import models as notification
from rancho.project.models import Project

# Basic operations for this app
####################################################################################

@login_required
def list(request, p_id, status = ''):
    user = request.user    
    project = get_object_or_404(Project, id = p_id)
    
    if not checkperm(PERMISSIONS_MILESTONE_VIEW, user, project ):
        return HttpResponseForbidden(_('Forbidden Access'))
    late_milestones = []
    upcoming_milestones = []
    complete_milestones = []
    if status == 'late' or not status:
        late_milestones = Milestone.objects.get_late_milestones(project = project)
    if status == 'upcoming' or not status:
        upcoming_milestones = Milestone.objects.get_upcoming_milestones(project = project)
    if status == 'complete' or not status:
        complete_milestones = Milestone.objects.get_complete_milestones(project = project)
    context = {
        'project': project,
        'late_milestones': late_milestones, 
        'upcoming_milestones': upcoming_milestones,
        'complete_milestones': complete_milestones,
        'view_alone': bool(status)
        }
    return render_to_response("milestone/milestones_list.html", context,
                              context_instance=RequestContext(request))

@login_required
def create(request, p_id):

    user = request.user
    project = get_object_or_404(Project, id = p_id)
    users_in_project = project.get_users()
    
    if not checkperm(PERMISSIONS_MILESTONE_CREATE, user, project ):        
        return HttpResponseForbidden(_('Forbidden Access'))
        
    users_to_notify = utils.get_users_to_notify(project, PERMISSIONS_MILESTONE_VIEW)
    
    if request.method == 'POST':
        form = NewMilestoneForm(utils.format_users_for_dropdown(user, users_to_notify), request.POST)

        if form.is_valid():
            mstone = form.save(user, project)

            if mstone.send_notification_email:
                #TODO: make a view milestone url to use here
                link_url = u"http://%s%s" % ( unicode(Site.objects.get_current()), urlresolvers.reverse('rancho.milestone.views.list', args = [p_id]))
                #link_url = u"http://%s%s" % ( unicode(Site.objects.get_current()), urlresolvers.reverse('rancho.message.views.read_add_comment', kwargs={'p_id': project.id, 'm_id':msg.id}),)
                if mstone.responsible: #just notify one person                                
                    notification.send([mstone.responsible], "milestone_new", {'link_url': link_url, 'milestone': mstone })
                else: #notify all users with perm
                    notification.send(users_to_notify, "milestone_new", {'link_url': link_url, 'milestone': mstone })
             
            events_log(user, 'A', mstone.title, mstone)   
            request.user.message_set.create(message=_('Milestone "%s" successfully created.') % mstone.title)
            return HttpResponseRedirect(urlresolvers.reverse('rancho.milestone.views.list', args = [p_id]))

    else:
        form = NewMilestoneForm(utils.format_users_for_dropdown(user, users_in_project))
        
    context = { 'project': project, 
               'newMilestone': form,
               }
               
    return render_to_response("milestone/create_milestone.html", context,
                                  context_instance=RequestContext(request))

@login_required    
def edit(request, p_id, milestone_id):
    
    user = request.user
    project = get_object_or_404(Project, id = p_id)
    milestone = get_object_or_404(Milestone, id = milestone_id)
    users_in_project = project.get_users()
    
    if not checkperm(PERMISSIONS_MILESTONE_EDITDELETE, user, project, milestone) or milestone.project != project:        
        return HttpResponseForbidden(_('Forbidden Access'))
    
    users_to_notify = utils.get_users_to_notify(project, PERMISSIONS_MILESTONE_VIEW)

    if request.method=='POST':
        form = NewMilestoneForm(utils.format_users_for_dropdown(user, users_to_notify), request.POST)
        
        if form.is_valid():
            
            user_id = int(form.cleaned_data['responsible'])
            if user_id != 0:
                milestone.responsible = get_object_or_404(User, id = user_id)
            else:
                milestone.responsible = None
                milestone.completion_date = None
            old_milestone_title = milestone.title
            milestone.title = form.cleaned_data['title']
            milestone.due_date = form.cleaned_data['due_date']
            milestone.send_notification_email = form.cleaned_data['send_notification_email'] 
            milestone.save()
            
            if milestone.send_notification_email:
                link_url = u"http://%s%s" % ( unicode(Site.objects.get_current()), urlresolvers.reverse('rancho.milestone.views.list', args = [p_id]))
                #link_url = u"http://%s%s" % ( unicode(Site.objects.get_current()), urlresolvers.reverse('rancho.message.views.read_add_comment', kwargs={'p_id': project.id, 'm_id':msg.id}),)
                if milestone.responsible: #just notify one person                                
                    notification.send([milestone.responsible], "milestone_updated", {'link_url': link_url, 'milestone': milestone, 'old_milestone_title': old_milestone_title})
                else: #notify entire project
                    notification.send(users_to_notify, "milestone_updated", {'link_url': link_url, 'milestone': milestone, 'old_milestone_title': old_milestone_title })

            events_log(user, 'U', milestone.title, milestone)
            request.user.message_set.create(message=_('Milestone successfully edited.'))
    else:
        responsible_index = 0
        if milestone.responsible:
            responsible_index = milestone.responsible.id
        data = {'title': milestone.title, 
                'due_date': milestone.due_date.date(),
                'responsible': responsible_index, 
                'send_notification_email': milestone.send_notification_email}
        form = NewMilestoneForm(utils.format_users_for_dropdown(user, users_in_project), data)
    
    context = {'project': project, 
               'milestone': milestone,
               'newMilestone': form,
               }
    return render_to_response("milestone/edit_milestone.html", context, context_instance = RequestContext(request))

        
@login_required        
def complete(request, p_id, milestone_id):
    user = request.user
    project = get_object_or_404(Project, id = p_id)
    milestone = get_object_or_404(Milestone, id = milestone_id)
    if not checkperm(PERMISSIONS_MILESTONE_VIEW, user, project ):        
        return HttpResponseForbidden(_('Forbidden Access'))
    if not milestone.completion_date:
        milestone.completion_date = date.today()
        milestone.responsible = user
        # PERMISSIONS
        milestone.save()
        events_log(user, 'COMP', milestone.title, milestone)
    return HttpResponseRedirect(urlresolvers.reverse('rancho.milestone.views.list', args = [p_id]))
          
@login_required        
def incomplete(request, p_id, milestone_id):
    user = request.user    
    project = get_object_or_404(Project, id = p_id)
    milestone = get_object_or_404(Milestone, id = milestone_id)
    if not checkperm(PERMISSIONS_MILESTONE_VIEW, user, project ):        
        return HttpResponseForbidden(_('Forbidden Access'))
    if milestone.completion_date:
        milestone.completion_date = None
        # PERMISSIONS
        milestone.save()
        events_log(user, 'ICOMP', milestone.title, milestone)
    return HttpResponseRedirect(urlresolvers.reverse('rancho.milestone.views.list', args = [p_id]))

@login_required    
def delete(request, p_id, milestone_id):
    user = request.user
    project = get_object_or_404(Project, id = p_id)
    milestone = get_object_or_404(Milestone, id = milestone_id)
    
    if not checkperm(PERMISSIONS_MILESTONE_EDITDELETE, user, project, milestone) or milestone.project != project:        
        return HttpResponseForbidden(_('Forbidden Access'))
    
    request.user.message_set.create(message=_('Milestone "%s" successfully deleted.') % milestone.title)
    events_log(user, 'D', milestone.title, milestone)
    milestone.delete()
    return HttpResponseRedirect(urlresolvers.reverse('rancho.milestone.views.list', args = [p_id]))
