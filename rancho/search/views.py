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

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from rancho.file.models import FileVersion, File
from rancho.message.models import Message
from rancho.milestone.models import Milestone
from rancho.project.models import Project
from rancho.search.forms import SearchForm
from rancho.wikiboard.models import WikiEntry
from rancho.haystack.query import SearchQuerySet
from rancho.granular_permissions.permissions import PERMISSIONS_MESSAGE_VIEW,\
    PERMISSIONS_WIKIBOARD_VIEW, PERMISSIONS_MILESTONE_VIEW,\
    PERMISSIONS_TODO_VIEW, PERMISSIONS_FILE_VIEW
from rancho.todo.models import ToDo
from rancho.tagging.models import TaggedItem
from django.db.models.query_utils import Q

WIKIBOARD = 'wikiboard'
MILESTONE = 'milestone'
FILE = 'file'
MESSAGE = 'message'

def search_object(user, project, query, perm, model):    
    if not user.is_superuser: #restrict to projects with perm
        if project: #restrict to given project        
            messages = SearchQuerySet().filter(content=query, project__exact=project.id).models(model)
        else:                
            perm = user.get_rows_with_permission(Project, perm)
            projs_ids = perm.values_list('object_id', flat=True)
            messages = SearchQuerySet().filter(content=query, project__in=projs_ids).models(model)
    else: #super user gets everything
        if project: #restrict to given project        
            messages = SearchQuerySet().filter(content=query, project__exact=project.id).models(model)
        else:
            messages = SearchQuerySet().filter(content=query).models(model)
    #now that we can get ids really db objects (not really sure about performance check latter)
    m = []
    for r in messages:
        m.append(r.pk)    
    return model.objects.filter(pk__in=m)

@login_required    
def search(request, p_id=None):
    user = request.user

    if p_id:
        project = get_object_or_404(Project, id=p_id)
        project.check_user_in_project_or_404(user)
    else:
        project=None
        
    messages = milestones = wikiboards = files = todos = []
    query = None
    select = None

    if request.method == 'GET':    
        form = SearchForm(request.GET)            
        if form.is_valid():    
            query = form.cleaned_data['query']
            select = request.GET.get('select', None)

            messagetagged = TaggedItem.objects.get_by_model(Message, query)
            ids1 =  list(messagetagged.values_list('id', flat=True))            
            messages = search_object(user, project, query, PERMISSIONS_MESSAGE_VIEW, Message)            
            ids2 =  list(messages.values_list('id', flat=True))            
            ids1.extend(ids2)
            messages = Message.objects.filter(id__in=ids1)
            
            
            filetagged = TaggedItem.objects.get_by_model(File, query)
            ids1 = []
            for f in filetagged:
                ids1.append(f.last_file_version_id)            
            files = search_object(user, project, query, PERMISSIONS_FILE_VIEW, FileVersion)
            ids2 =  list(files.values_list('id', flat=True))            
            ids1.extend(ids2)
            files = FileVersion.objects.filter(id__in=ids1)

                        
            todos = search_object(user, project, query, PERMISSIONS_TODO_VIEW, ToDo)            
            wikiboards = search_object(user, project, query, PERMISSIONS_WIKIBOARD_VIEW, WikiEntry)
            milestones = search_object(user, project, query, PERMISSIONS_MILESTONE_VIEW, Milestone)
            
    else:
        form = SearchForm(request.GET) 
    
    return render_to_response('search/search.html', 
                              {'form': form,
                                'project':project,                               
                               'messages': messages,
                               'todos': todos,
                               'wikiboards': wikiboards,
                               'files': files,
                               'milestones': milestones,
                               'results': list(messages) + list(wikiboards) + list(todos) + list(files) + list(milestones),
                               'query': query,
                               'select': select
                               },
                               context_instance=RequestContext(request))
