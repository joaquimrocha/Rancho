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
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.shortcuts import get_object_or_404

from rancho.milestone.models import Milestone
from rancho.message.models import Message
from rancho.project.models import Project
from rancho.search.forms import SearchForm
from rancho.wikiboard.models import Wiki
from rancho.granular_permissions.permissions import PERMISSIONS_WIKIBOARD_VIEW, PERMISSIONS_MESSAGE_VIEW, PERMISSIONS_FILE_VIEW
from rancho.file.models import File

WIKIBOARD = 'wikiboard'
MILESTONE = 'milestone'
FILE = 'file'
MESSAGE = 'message'

@login_required    
def search(request, p_id=None):
    user = request.user

    if p_id:
        project = get_object_or_404(Project, id=p_id)
        project.check_user_in_project_or_404(user)
    else:
        project=None
        
    messages = milestones = wikiboards = files = []
    query = None
    select = None

    if request.method == 'GET':    
        form = SearchForm(request.GET)            
        if form.is_valid():    
            query = form.cleaned_data['query']
            select = request.GET.get('select', None)
            if select:
                select = select.split(',')[0]

            messages = Message.objects.search(user, query, project)

            wikiboards = Wiki.objects.search(user, query, project)

            files = File.objects.search(user, query, project)

            milestones = Milestone.objects.search(user, query, project)
            
    else:
        form = SearchForm(request.GET) 
    
    return render_to_response('search/search.html', 
                              {'form': form,
                                'project':project,                               
                               'messages': messages,
                               'wikiboards': wikiboards,
                               'files': files,
                               'milestones': milestones,
                               'results': list(messages) + list(wikiboards) + list(files) + list(milestones),
                               'query': query,
                               'select': select
                               },
                               context_instance=RequestContext(request))
