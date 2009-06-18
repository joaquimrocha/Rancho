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
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core import urlresolvers
from django.utils.translation import ugettext as _
from django.http import HttpResponseForbidden
from django.contrib.sites.models import Site

from rancho.message.forms import MessageForm, CommentForm
from rancho.message.models import Message
from rancho.project.models import Project
from rancho.granular_permissions.permissions import PERMISSIONS_MESSAGE_CREATE, PERMISSIONS_MESSAGE_VIEW, PERMISSIONS_MESSAGE_EDITDELETE
from rancho.granular_permissions.permissions import checkperm
from rancho.tagging.models import TaggedItem, Tag
from rancho.lib import utils
from rancho.notification import models as notification
from rancho.lib.utils import events_log

# Basic operations for this app
####################################################################################

@login_required
def list(request,p_id, tag=None):
    '''
    List all messages from a project
    '''    
    
    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    project.check_user_in_project_or_404(user)    
    users_in_project = project.get_users()
        
    if not checkperm(PERMISSIONS_MESSAGE_VIEW, user, project ):
        return HttpResponseForbidden(_('Forbidden Access'))
    
    #Get all the messages, except the ones that are comments
    if tag:
        tag = "\"%s\""%tag
        messagelist = TaggedItem.objects.get_by_model(Message, tag)
    else:
        messagelist = Message.objects
    messagelist = messagelist.filter(project=project).extra(where=['message_message.initial_message_id = message_message.id']).order_by('-creation_date')
        
    message_tags = Tag.objects.cloud_for_model(Message, steps=6, filters=dict(project=project))
        
    context = {'project': project,
               'users_in_project': users_in_project,
               'message_tags': message_tags,
               'messagelist': messagelist }
    return render_to_response('message/message_list.html', 
                              context,
                              context_instance=RequestContext(request))    
     
    
@login_required    
def create(request,p_id):
    '''
    Creates a new message
    '''    
    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    project.check_user_in_project_or_404(user)    
    users_in_project = project.get_users()
    
    if not checkperm(PERMISSIONS_MESSAGE_CREATE, user, project ):        
        return HttpResponseForbidden(_('Forbidden Access'))
        
    tags = utils.get_site_tags(project)
    
    users_to_notify = utils.get_users_to_notify(project, PERMISSIONS_MESSAGE_VIEW)
    
    if request.method == 'POST':        
        form = MessageForm(users_to_notify,tags, request.POST)
        if form.is_valid():
            msg = form.save(user, project)
             
            link_url = u"http://%s%s" % ( unicode(Site.objects.get_current()), urlresolvers.reverse('rancho.message.views.read_add_comment', kwargs={'p_id': project.id, 'm_id':msg.id}),)
            notification.send(msg.notify_to.all(), "message_new", {'link_url': link_url, 'message': msg })
                        
            request.user.message_set.create(message=_("Message Created"))            
            events_log(user, 'A', msg.title, msg)
            return HttpResponseRedirect(urlresolvers.reverse('rancho.message.views.list', args=[project.id]))
    else:
        form = MessageForm(users_to_notify, tags)
     
    context = {'project': project,
               'users_in_project': users_in_project,
               'form': form }   
    return render_to_response("message/new_message.html", context,
                              context_instance=RequestContext(request)
                              )

@login_required    
def edit(request,p_id,m_id):

    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    message = get_object_or_404(Message, pk=m_id)
    project.check_user_in_project_or_404(user)
    users_in_project = project.get_users()
    
    if not checkperm(PERMISSIONS_MESSAGE_EDITDELETE, user, project, message ) or message.project != project:
        return HttpResponseForbidden(_('Forbidden Access'))
    
    tags = utils.get_site_tags(project)
    
    if request.method == 'POST':        
        if message.initial_message == message:            
            form=MessageForm(project.get_users(), tags, request.POST) 
        else:
            form=CommentForm(request.POST)
             
        if form.is_valid():   
            form.save(user, project, message)            
            events_log(user, 'U', message.title, message)            
            
            if message.initial_message == message:
                return HttpResponseRedirect(urlresolvers.reverse('rancho.message.views.list', args=[project.id]))
            else:
                return HttpResponseRedirect(urlresolvers.reverse('rancho.message.views.read_add_comment', kwargs={'p_id': project.id, 'm_id': message.initial_message.id}))
    else: 
        data = {'title':message.title,
                'message':message.body
                }
        if message.initial_message == message:
            data['tags'] = message.tags                        
            form=MessageForm(project.get_users(), tags, data) 
        else:
            form=CommentForm(data)

    context = {'project': project,
               'users_in_project': users_in_project,
               'form': form,
               'edit_initial': isinstance(form, MessageForm),
               'message': message
                }   
    return render_to_response("message/edit_message.html", context,
                              context_instance=RequestContext(request))
                    


@login_required
def delete(request,p_id,m_id):    

    user = request.user    
    project = get_object_or_404(Project, pk=p_id)
    message = get_object_or_404(Message, pk=m_id)
    project.check_user_in_project_or_404(user)
    
    if not checkperm(PERMISSIONS_MESSAGE_EDITDELETE, user, project, message ) or message.project != project:
        return HttpResponseForbidden(_('Forbidden Access'))

    
    kw = {'m_id': message.initial_message.id, 'p_id': project.id}

    events_log(user, 'D', message.title, message)
    
    if message.initial_message == message: #delete main thread
        Message.objects.filter(initial_message=message.initial_message).delete()
    else:
        message.delete()
                
    request.user.message_set.create(message=_("Message Deleted."))         
    
    page = request.GET.get('page')
    if page == 'msg':
        return HttpResponseRedirect(urlresolvers.reverse('rancho.message.views.read_add_comment', kwargs=kw))
    else:
        return HttpResponseRedirect(urlresolvers.reverse('rancho.message.views.list', args=[project.id]))
        
    

    
# other functions (realated to urls)
####################################################################################

@login_required
def read_add_comment(request,p_id,m_id):

    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    message = get_object_or_404(Message, pk=m_id)
    project.check_user_in_project_or_404(user)
    users_in_project = project.get_users()
    
    if not checkperm(PERMISSIONS_MESSAGE_VIEW, user, project ) or message.project != project :
        return HttpResponseForbidden(_('Forbidden Access'))
    
    #if not initial message redirect to id
    if message.initial_message != message:
        return HttpResponseRedirect(urlresolvers.reverse('rancho.message.views.read_add_comment', kwargs={'p_id': project.id, 'm_id':message.initial_message.id}))    

    message.read_by.add(user)

    if request.method == 'POST':     
        if not checkperm(PERMISSIONS_MESSAGE_CREATE, user, project ) or message.project != project :
            return HttpResponseForbidden(_('Forbidden Access'))
       
        form=CommentForm(request.POST)
        if form.is_valid():
            msg = form.save(user, project, message, True)
            
            message.read_by.clear()
            
            link_url = u"http://%s%s" % ( unicode(Site.objects.get_current()), urlresolvers.reverse('rancho.message.views.read_add_comment', kwargs={'p_id': project.id, 'm_id':msg.id}),)
            notification.send(msg.initial_message.notify_to.all(), "message_replied", {'link_url': link_url, 'message': msg })
            
            return HttpResponseRedirect(urlresolvers.reverse('rancho.message.views.read_add_comment', kwargs={'m_id': message.id, 'p_id': project.id}))
    else:
        form = CommentForm()
     
    
     
    context = {'project': project,
               'message': message,
               'users_in_project': users_in_project,               
               'original_message': message.initial_message,
               'allmessages': Message.objects.filter(initial_message=message.initial_message).exclude(id=message.id).order_by('-creation_date'),
               'form': form }       
    return render_to_response("message/read_message.html", context,
                              context_instance=RequestContext(request))    
    
