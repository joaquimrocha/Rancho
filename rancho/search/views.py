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

from rancho.message.models import Message
from rancho.project.models import Project
from rancho.search.forms import SearchForm
from rancho.wikiboard.models import WikiEntry
from rancho.granular_permissions.permissions import PERMISSIONS_WIKIBOARD_VIEW, PERMISSIONS_MESSAGE_VIEW, PERMISSIONS_FILE_VIEW
from rancho.file.models import FileVersion

@login_required    
def search(request, p_id=None):
    user = request.user

    if p_id:
        project = get_object_or_404(Project, id=p_id)
        project.check_user_in_project_or_404(user)
    else:
        project=None
        
    messages = wikiboards = files = []

    if request.method == 'POST':    
        form = SearchForm(request.POST)            
        if form.is_valid():    
            query = form.cleaned_data['query']
            
            #print File.index.search( query ).values_list('last_file_version',flat=True)
            
            #search messages
            messages = Message.index.search( query )        
            if not user.is_superuser: #restrict to projects with perm                
                perm = user.get_rows_with_permission(Project, PERMISSIONS_MESSAGE_VIEW)
                projs_ids = perm.values_list('object_id', flat=True)
                messages = messages.filter(project__in=projs_ids)    
            if project: #restrict to given project        
                messages = messages.filter(project=project)
            
            #search wikiboards
            wikiboards = WikiEntry.index.search( query )        
            if not user.is_superuser: #restrict to projects with perm                
                perm = user.get_rows_with_permission(Project, PERMISSIONS_WIKIBOARD_VIEW)
                projs_ids = perm.values_list('object_id', flat=True)
                wikiboards = wikiboards.filter(wiki__project__in=projs_ids)    
            if project: #restrict to given project        
                wikiboards = wikiboards.filter(wiki__project=project)
            
            #TODO: no way to merge files... shit
            #search files
            fileversion = FileVersion.index.search( query )
            #file = File.index.search( query )  
            if not user.is_superuser: #restrict to projects with perm
                perm = user.get_rows_with_permission(Project, PERMISSIONS_FILE_VIEW)
                projs_ids = perm.values_list('object_id', flat=True)
                fileversion = fileversion.filter(file__project__in=projs_ids)
                #file = file.filter(project__in=projs_ids)    
            if project: #restrict to given project        
                fileversion = fileversion.filter(file__project=project)
                #file = file.filter(project=project)
            #TODO: this should use values list... change this when code is fixed
            
            #ids = [file['last_file_version_id'] for file in file.values()]            
            #file = FileVersion.objects.filter(id__in=ids)            
            #files = (fileversion | file).distinct()
            files = fileversion
            
    else:        
        form = SearchForm(request.GET) 
    
    return render_to_response('search/search.html', 
                              {'form': form,
                                'project':project,                               
                               'messages': messages[:5],
                               'wikiboards': wikiboards[:5],
                               'files': files[:5]},
                              context_instance=RequestContext(request))


