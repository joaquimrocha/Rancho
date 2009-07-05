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

from StringIO import StringIO
from django.contrib.auth.decorators import login_required
from django.core import urlresolvers
from django.http import HttpResponseRedirect, HttpResponse, \
    HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from rancho.granular_permissions.permissions import PERMISSIONS_WIKIBOARD_VIEW, \
    PERMISSIONS_WIKIBOARD_CREATE, PERMISSIONS_WIKIBOARD_EDITDELETE, checkperm
from rancho.lib.utils import events_log
from rancho.project.models import Project
from rancho.wikiboard.forms import NewWikiEntryForm, TinyMceForm
from rancho.wikiboard.models import Wiki, WikiEntry
import ho.pisa as pisa


# Basic operations for this app
####################################################################################

@login_required
def list(request, p_id):

    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    project.check_user_in_project_or_404(user)    
    users_in_project = project.get_users()

    if not checkperm(PERMISSIONS_WIKIBOARD_VIEW, user, project ):
        return HttpResponseForbidden(_('Forbidden Access'))
    
    wikis = Wiki.objects.filter(project=project).order_by('-last_version')
    
    
    context = {'project': project,
               'users_in_project': users_in_project,
               'wikis': wikis }
    return render_to_response('wikiboard/list_wiki.html', 
                              context,
                              context_instance=RequestContext(request))

@login_required
def create(request, p_id):

    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    project.check_user_in_project_or_404(user)    
    users_in_project = project.get_users()
    
    if not checkperm(PERMISSIONS_WIKIBOARD_CREATE, user, project ):
        return HttpResponseForbidden(_('Forbidden Access'))

     
    if request.method=='POST':        
        form = NewWikiEntryForm(request.POST)                   
        if form.is_valid():
            
            #TODO: put in form save  
            wiki = Wiki()
            wiki.project = project
            wiki.creator = user
            wiki.name = form.cleaned_data['wiki_name']
            wiki.save()
            
            wikientry = WikiEntry()
            wikientry.content = form.cleaned_data['content']
            wikientry.author = user
            wikientry.wiki = wiki            
            wikientry.save()
            wiki.last_version = wikientry
            wiki.save()
            
            events_log(user, 'A', wiki.name, wikientry)
            request.user.message_set.create(message=_('Wikiboard "%s" was successfully created.') % wiki.name)
                        
            kw = {'p_id': project.id, 'entry_id': wiki.id, 'entry_version': wikientry.id}
            return HttpResponseRedirect(urlresolvers.reverse('rancho.wikiboard.views.view_page', kwargs=kw))                
    else:
        form = NewWikiEntryForm()
    
    context = {'project': project,
               'users_in_project': users_in_project,
               'form': form }
    return render_to_response("wikiboard/create_entry.html", context,
                              context_instance=RequestContext(request)) 
    
@login_required               
def edit(request, p_id,entry_id=None,entry_version=None):

    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    project.check_user_in_project_or_404(user)    
    users_in_project = project.get_users()
    
    if entry_id and entry_version:
        wiki = get_object_or_404(Wiki, pk=entry_id)
        wikicurentry = get_object_or_404(WikiEntry, id=entry_version)
        
        if not checkperm(PERMISSIONS_WIKIBOARD_CREATE, user, project, wiki ) or wiki.project != project:
            return HttpResponseForbidden(_('Forbidden Access'))
        
    
    if request.method=='POST':        
        tinyMceForm = TinyMceForm(request.POST)        
        if tinyMceForm.is_valid():            
                        
            wikientry = WikiEntry()
            wikientry.content = tinyMceForm.cleaned_data['content']
            wikientry.author = user
            wikientry.wiki = wiki
            wikientry.save()
            wiki.last_version = wikientry
            wiki.save()
            
            events_log(user, 'U', wiki.name, wikientry)
            
            request.user.message_set.create(message=_('Wikiboard "%s" was successfully updated.') % wiki.name)
            kw = {'p_id': project.id, 'entry_id': wiki.id, 'entry_version': wikientry.id}
            return HttpResponseRedirect(urlresolvers.reverse('rancho.wikiboard.views.view_page', kwargs=kw))
                
    else:
        if wiki:
            data = {'content': wikicurentry.content}
        else:
            data = {}

        tinyMceForm = TinyMceForm(data)

    context = {'project': project,
               'users_in_project': users_in_project,
               'wiki': wiki,
               'wikicurentry': wikicurentry,
               'wiki_entrys': WikiEntry.objects.filter(wiki=wiki).order_by('-creation_date'),
               'form': tinyMceForm }
    return render_to_response("wikiboard/edit_entry.html", context,
                              context_instance=RequestContext(request)) 
  
            
                
@login_required        
def delete(request,p_id,entry_id):

    user = request.user    
    project = get_object_or_404(Project, pk=p_id)
    wiki = get_object_or_404(Wiki, pk=entry_id)
    project.check_user_in_project_or_404(user)
    
    if not checkperm(PERMISSIONS_WIKIBOARD_EDITDELETE, user, project, wiki ) or wiki.project != project:
        return HttpResponseForbidden(_('Forbidden Access'))        
    
    events_log(user, 'D', wiki.name, wiki)
    user.message_set.create(message = _('The Wikiboard "%s" has been successfully deleted.') % wiki.name)
    wiki.delete()

    return HttpResponseRedirect(urlresolvers.reverse('rancho.wikiboard.views.list', args=[p_id]))
    
    
# other functions (realated to urls)
####################################################################################
    
@login_required
def view_page(request, p_id,entry_id,entry_version):

    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    project.check_user_in_project_or_404(user)    
    users_in_project = project.get_users()
    
    if not checkperm(PERMISSIONS_WIKIBOARD_VIEW, user, project, None ):
        return HttpResponseForbidden(_('Forbidden Access'))
        

    wiki = get_object_or_404(Wiki, id=entry_id)
    wikicurentry = get_object_or_404(WikiEntry, id=entry_version)
    wiki_entries = WikiEntry.objects.filter(wiki=wiki).order_by('-creation_date')
    
    context = {'project': project,
               'users_in_project': users_in_project,
               'wiki': wiki,
               'wikicurentry': wikicurentry,
               'wiki_entries':wiki_entries }
    
    return render_to_response('wikiboard/view.html', 
                              context,
                              context_instance=RequestContext(request))
    
    
@login_required        
def export_wiki(request,p_id,entry_id,entry_version, file_type):
    user = request.user
    project = get_object_or_404(Project, pk=p_id)
    project.check_user_in_project_or_404(user)    

    wiki = get_object_or_404(Wiki, id=entry_id)
    wikicurentry = get_object_or_404(WikiEntry, id=entry_version)
    
    if not checkperm(PERMISSIONS_WIKIBOARD_VIEW, user, project ):
        return HttpResponseForbidden(_('Forbidden Access'))

    text  = u"<h1>%s</h1> %s"%(wiki.name,wikicurentry.content)
    html = u"""
<html>
<style>
@page {
   margin: 1cm;
   @frame footer {
     -pdf-frame-content: footerContent;
     bottom: 1cm;
     margin-left: 1cm;
     margin-right: 1cm;
     height: 1cm;
     text-align: center;
   }
}
</style>
<body>
  %s
  <div id="footerContent"  align="right">
     <pdf:pagenumber> 
  </div>
</body>
</html>
"""%text
            
    if file_type == 'pdf':
        result = StringIO()
        pdf = pisa.pisaDocument(StringIO(html.encode("ISO-8859-1")), result)
        if not pdf.err:
            return HttpResponse(result.getvalue(), mimetype='application/pdf')
        return HttpResponseServerError(_('Could not generate pdf file.'))
    
    elif file_type == 'html':
        response = HttpResponse(mimetype='text/html')
        response.write(html)
        return response
