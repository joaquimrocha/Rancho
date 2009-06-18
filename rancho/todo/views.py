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

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
from django.http import HttpResponseForbidden
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.core import urlresolvers
from django.template import loader, Context

from rancho.todo.models import ToDoList, ToDo
from rancho.project.models import Project
from rancho.todo.forms import NewToDoListForm, EditToDoListForm, EditToDoForm
from rancho.user.models import User
from rancho.lib import utils
from rancho.notification import models as notification
from rancho.granular_permissions.permissions import PERMISSIONS_TODO_VIEW, PERMISSIONS_TODO_CREATE, PERMISSIONS_TODO_EDITDELETE
from rancho.granular_permissions.permissions import checkperm
from rancho.lib.utils import events_log

import datetime


@login_required
def list(request, p_id):    
    user = request.user
    project = get_object_or_404(Project, id = p_id)
    
    if not checkperm(PERMISSIONS_TODO_VIEW, user, project ):
        return HttpResponseForbidden(_('Forbidden Access'))
    
    users_in_project = project.get_users()
    todo_list = ToDoList.objects.filter(project = project)
    context = {
        'users_in_project': utils.format_users_for_dropdown(user, users_in_project),
        'project': project,
        'todo_lists': [],
        }
    for l in todo_list:
        context['todo_lists'].append((l, l.get_todos()))
    
    
    return render_to_response('todo/todos_list.html', context,
                              context_instance = RequestContext(request))

@login_required
def view_todo_list(request, p_id, todo_list_id):
    
    user = request.user
    project = get_object_or_404(Project, id = p_id)
    todo_list = get_object_or_404(ToDoList, id = todo_list_id)
    
    if not checkperm(PERMISSIONS_TODO_VIEW, user, project ):
        return HttpResponseForbidden(_('Forbidden Access'))
    
    users_in_project = project.get_users()
    context = {
               'users_in_project': utils.format_users_for_dropdown(user, users_in_project),
               'project': project,
               'todo_lists': [(todo_list, todo_list.get_todos())],
               'view_alone': True,
               }
    return render_to_response('todo/todos_list.html', context,
                              context_instance = RequestContext(request))

@login_required
def create(request, p_id):

    user = request.user    
    project = get_object_or_404(Project, id = p_id)
    
    if not checkperm(PERMISSIONS_TODO_CREATE, user, project):
        return HttpResponseForbidden(_('Forbidden Access'))
    
    users_in_project = project.get_users()
    context = {}
    context['users_in_project'] = users_in_project
    context['project'] = project
    project.check_user_in_project_or_404(user)
    newTDLform = NewToDoListForm()
    if request.method=='POST':
        newTDLform = NewToDoListForm(request.POST)
        if newTDLform.is_valid():
            context['project'] = project
            #TODO: ROCHA: put this into a form method
            todo_list = ToDoList()
            todo_list.creator = user
            todo_list.project = project
            
            todo_list.title = newTDLform.cleaned_data['todolist_name']
            todo_list.description = newTDLform.cleaned_data['todolist_description']
            todo_list.save()
            
            events_log(user, 'A', todo_list.title, todo_list)
            request.user.message_set.create(message=_('ToDo list "%(todo_list_name)s" successfully created.') % {'todo_list_name': todo_list.title})
            return HttpResponseRedirect(urlresolvers.reverse('rancho.todo.views.list', args = [p_id]))
    context['newTDLform'] = newTDLform
    return render_to_response('todo/new_todo_list.html', context,
                              context_instance=RequestContext(request))


@login_required
def add_todo(request, p_id, todo_list):    
    user = request.user
    project = get_object_or_404(Project, id = p_id)
    todo_list = get_object_or_404(ToDoList, id = todo_list)
    
    if not checkperm(PERMISSIONS_TODO_CREATE, user, project):
        return HttpResponseForbidden(_('Forbidden Access'))
    
    if request.method == 'GET':
        try:
            todo_desc = request.GET.get('todo_desc')
            todo_responsible = int(request.GET.get('todo_responsible'))
        except:
            return HttpResponseRedirect(urlresolvers.reverse('rancho.todo.views.list', args = [p_id]))
        if not todo_desc:
            result = """<taconite>
                            <show select="#empty_todo_error{{ todo_list }}"/>
                        </taconite>"""
            result = loader.get_template_from_string(result).render(Context({'todo_list': todo_list.id}))
            return HttpResponse(result, mimetype='text/xml')
        if todo_responsible:
            todo_responsible = get_object_or_404(User, pk = todo_responsible)
        todo = ToDo()
        todo.creator = user
        if todo_responsible != 0:
            todo.responsible = todo_responsible
        todo.description = todo_desc
        todo.todo_list = todo_list
        todo.save()
        todo_list.number_of_todos+=1
        todo_list.save()
        todo.position = todo_list.number_of_todos + 1
        todo.save()
        
        events_log(user, 'A', todo.description, todo)
        
        #notify all users with perm
        link_url = u"http://%s%s" % ( unicode(Site.objects.get_current()), urlresolvers.reverse('rancho.todo.views.view_todo_list', kwargs={'p_id': project.id, 'todo_list_id': todo_list.id}),)
        if todo.responsible: #just notify one person                                
            notification.send([todo.responsible], "todo_new", {'link_url': link_url, 'todo': todo, 'project': project, 'todo_list': todo_list})
        else: #notify all users with perm
            users_to_notify = utils.get_users_to_notify(project, PERMISSIONS_TODO_VIEW)
            notification.send(users_to_notify, "todo_new", {'link_url': link_url, 'todo': todo, 'project': project, 'todo_list': todo_list})

        
        result = """<taconite>
                    {% load displaytodo %}
                    <append select="#todos{{todo_list}}">
                        <div id="edit_todo{{todo.id}}" {% ifequal user todo.responsible %}style="background: #EBF0FA;"{% endifequal %}>
                        {% displaytodo todo user %}
                        </div>
                        <script type="text/javascript">
                            $("#check{{todo.id}}_link").click(
                                function(){
                                    $.get("{% url todo.views.switch_todo_status project.id %}", {todo: {{todo.id}} });
                                    $("img#check{{todo.id}}").attr({
                                        src: "/media/basepage/images/check.png"
                                        });
                                    return false;
                                }
                            );
                        </script>
                    </append>
                    <attr select="input#todo_desc{{ todo_list }}" name="value" value=""/>
                    <hide select="#empty_todo_error{{ todo_list }}" />
                    </taconite>
                    """
        result = loader.get_template_from_string(result).render(Context({'todo_list': todo_list.id, 'user': user, 'todo': todo, 'project': project}))
        return HttpResponse(result, mimetype='text/xml')

@login_required        
def edit_todo(request, p_id, todo_id):
    
    user = request.user
    project = get_object_or_404(Project, id = p_id)
    todo = get_object_or_404(ToDo, id = todo_id)
    todo_list = todo.todo_list
    
    if not checkperm(PERMISSIONS_TODO_EDITDELETE, user, project, todo) or todo_list.project != project:
        return HttpResponseForbidden(_('Forbidden Access'))
    
    users_in_project = utils.format_users_for_dropdown(user, project.get_users())
    context = {'project': project, 'todo': todo, 'todo_list': todo_list}
    if request.method == 'POST':
        edit_todo_form = EditToDoForm(users_in_project, request.POST)
        context['edit_todo_form'] = edit_todo_form
        if edit_todo_form.is_valid():
            user_id = int(edit_todo_form.cleaned_data['responsible'])
            if user_id != 0:
                todo.responsible = get_object_or_404(User, id = user_id)
            else:
                todo.responsible = None
            todo.description = edit_todo_form.cleaned_data['title']
            todo.save()
            
            events_log(user, 'U', todo.description, todo)
            request.user.message_set.create(message=_('ToDo item successfully updated.'))
        return render_to_response('todo/edit_todo.html', context,
                      context_instance=RequestContext(request))
    responsible_index = 0
    if todo.responsible:
        responsible_index = todo.responsible.id
    data = {'title': todo.description, 'responsible': responsible_index}
    edit_todo_form = EditToDoForm(users_in_project, data)
    context['edit_todo_form'] = edit_todo_form
    return render_to_response('todo/edit_todo.html', context,
                          context_instance=RequestContext(request))
 
@login_required   
def save_changes(request, p_id):
    user = request.user
    project = get_object_or_404(Project, id = p_id)
    
    if request.method == 'POST':
        todo = get_object_or_404(ToDo, id = int(request.POST.get('todo')))
        todo_list = todo.todo_list
        
        if not checkperm(PERMISSIONS_TODO_EDITDELETE, user, project, todo) or todo_list.project != project:
            return HttpResponseForbidden(_('Forbidden Access'))
        
        responsible_id = int(request.POST.get('responsible'))
        if responsible_id:
            responsible = get_object_or_404(User, id = responsible_id)
        else:
            responsible = None
        description = request.POST.get('description')
        todo.responsible = responsible
        if description:
            todo.description = description
        todo.save()
        
        events_log(user, 'U', todo.description, todo)
        
        result = loader.get_template('todo/display_todo.html').render(Context({'todo': todo}))
        return HttpResponse(result, mimetype='text/xml')
    return HttpResponseRedirect(urlresolvers.reverse('rancho.todo.views.list', args = [p_id]))

@login_required
def delete_todo_list(request, p_id):

    #TODOS: Need to delete todo in todo list
    user = request.user
    project = get_object_or_404(Project, id = p_id)
    if request.method == 'GET':
        todo_list = get_object_or_404(ToDoList, id = int(request.GET.get('todo_list')))
        
        if not checkperm(PERMISSIONS_TODO_EDITDELETE, user, project, todo_list) or todo_list.project != project:
            return HttpResponseForbidden(_('Forbidden Access'))
        
        request.user.message_set.create(message=_('ToDo list "%(todo_list_name)s" deleted.') % {'todo_list_name': todo_list.title})
        todo_list.delete()
        
        events_log(user, 'D', todo_list.title, todo_list)
    return HttpResponseRedirect(urlresolvers.reverse('rancho.todo.views.list', args = [p_id]))

@login_required
def delete_todo(request, p_id):

    #TODOS: Need to delete todo in todo list
    user = request.user
    project = get_object_or_404(Project, id = p_id)
    if request.method == 'GET':
        todo_item = get_object_or_404(ToDo, id = int(request.GET.get('todo')))
        todo_list = todo_item.todo_list
        
        if not checkperm(PERMISSIONS_TODO_EDITDELETE, user, project, todo_item) or todo_list.project != project:
            return HttpResponseForbidden(_('Forbidden Access'))
        
        todo_item.delete()
        events_log(user, 'D', todo_item.description, todo_item)
        
        return HttpResponseRedirect(urlresolvers.reverse('rancho.todo.views.list', args = [p_id]))
    else:
        return HttpResponseRedirect(urlresolvers.reverse('rancho.todo.views.list', args = [p_id]))

@login_required
def switch_todo_status(request, p_id):

    user = request.user
    project = get_object_or_404(Project, id = p_id)
    if request.method=='GET':
        todo = get_object_or_404(ToDo, id=int(request.GET.get('todo')))
        
        if not checkperm(PERMISSIONS_TODO_VIEW, user, project):
            return HttpResponseForbidden(_('Forbidden Access'))
        
        if todo.completion_date != None:
            todo.completion_date = None
            
            events_log(user, 'ICOMP', todo.description, todo)
        else:
            todo.completion_date = datetime.datetime.now()
            todo.responsible = user
            
            events_log(user, 'COMP', todo.description, todo)
            
        todo.save()
        result = loader.get_template('todo/display_todo.html').render(Context({'todo':todo}))
        return HttpResponse(result, mimetype='text/xml')
    else:
        return HttpResponseRedirect(urlresolvers.reverse('rancho.todo.views.list', args = [p_id]))

@login_required
def edit_todo_list(request, p_id, todo_list_id):

    user = request.user
    project = get_object_or_404(Project, id = p_id)
    edit_todo_list = get_object_or_404(ToDoList, id = todo_list_id)
    
    if not checkperm(PERMISSIONS_TODO_EDITDELETE, user, project, edit_todo_list)  or edit_todo_list.project != project:
            return HttpResponseForbidden(_('Forbidden Access'))
    
    context = {'todo_list': edit_todo_list, 'project': project}
    if request.method == 'POST':
        data = request.POST.copy()
        edit_todo_list_form = EditToDoListForm(data)
        context['edit_todo_list_form'] = edit_todo_list_form
        if edit_todo_list_form.is_valid():
            edit_todo_list.title = edit_todo_list_form.cleaned_data['todolist_name']
            edit_todo_list.description = edit_todo_list_form.cleaned_data['todolist_description']
            edit_todo_list.save()
            
            events_log(user, 'U', edit_todo_list.title, edit_todo_list)
            request.user.message_set.create(message=_('ToDo list successfully updated.'))

        return render_to_response('todo/edit_todo_list.html', 
                                  context,
                                  context_instance=RequestContext(request))
    data = {'todolist_name': edit_todo_list.title, 'todolist_description': edit_todo_list.description}
    edit_todo_list_form = EditToDoListForm(data)
    context['edit_todo_list_form'] = edit_todo_list_form
    return render_to_response('todo/edit_todo_list.html', context,
                              context_instance=RequestContext(request))

