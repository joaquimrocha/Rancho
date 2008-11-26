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
from django.http import HttpResponseRedirect
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template import loader
from django.template.context import Context
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404
from django.template.loader import render_to_string

from rancho.user.forms import NewUserForm, EditUserForm 
from rancho.project.models import Project
from rancho.company.models import Company
from rancho.lib.templatetags.usernamegen import usernamegen
from rancho.milestone.models import Milestone
from rancho.granular_permissions.permissions import checkperm, PERMISSIONS_MILESTONE_VIEW, PERMISSIONS_TODO_VIEW, PERMISSIONS_MESSAGE_VIEW, PERMISSIONS_WIKIBOARD_VIEW, PERMISSIONS_FILE_VIEW
from rancho.lib import utils

from rancho import settings

# favour django-mailer but fall back to django.core.mail
try:
    from mailer import send_mail
except ImportError:
    from django.core.mail import send_mail

        
@login_required    
def dashboard(request):
    
    user = request.user            
    activeprojects = Project.objects.get_projects_for_user(user, status='A')
    finishedprojects = Project.objects.get_projects_for_user(user, status='F')
    frozenprojects = Project.objects.get_projects_for_user(user, status='Z')
    general_overview = []
    for project in activeprojects:
        general_overview.append((project, utils.get_overview(user, project)))
    return render_to_response('dashboard/dashboard.html', 
                              {'activeprojects': activeprojects, 
                               'finishedprojects': finishedprojects,
                               'frozenprojects': frozenprojects,
                               'general_overview': general_overview},
                              context_instance=RequestContext(request))

@login_required
def milestones(request):
    
    user = request.user            
    active_projects = Project.objects.get_projects_for_user(user, status='A')
    projects = []
    for project in active_projects:
        if not checkperm(PERMISSIONS_MILESTONE_VIEW, user, project ):
            continue
        upcoming_milestones = Milestone.objects.get_upcoming_milestones(project = project, user = user)
        late_milestones = Milestone.objects.get_late_milestones(project = project, user = user)
        if upcoming_milestones or late_milestones:
            projects.append({'project': project, 'late_milestones': late_milestones, 'upcoming_milestones': upcoming_milestones})
    return render_to_response('dashboard/milestones.html', 
                              {'projects': projects},
                              context_instance = RequestContext(request))
    
@login_required
def statistics(request):
    
    user = request.user            
    active_projects = Project.objects.get_projects_for_user(user, status='A')
    projects = []
    for project in active_projects:
        if checkperm(PERMISSIONS_MESSAGE_VIEW, user, project ):
            nummessages = project.message_set.count()   
        else:
            nummessages = -1
        if checkperm(PERMISSIONS_TODO_VIEW, user, project ):
            numtodos = project.todolist_set.count()
        else:
            numtodos = -1
        if checkperm(PERMISSIONS_MILESTONE_VIEW, user, project ):
            nummilestones = project.milestone_set.count()
        else:
            nummilestones = -1
        if checkperm(PERMISSIONS_WIKIBOARD_VIEW, user, project ):
            numwikiboards = project.wiki_set.count()
        else:
            numwikiboards = -1
        if checkperm(PERMISSIONS_FILE_VIEW, user, project ):
            numfiles = project.file_set.count() 
        else:
            numfiles = -1

        data={'project': project, 'messages': nummessages, 
              'todos': numtodos, 'milestones': nummilestones, 
              'wikiboards': numwikiboards, 'files': numfiles, }
        projects.append( data )
        
    return render_to_response('dashboard/statistics.html', 
                              {'projects': projects},
                              context_instance = RequestContext(request))


@login_required
@user_passes_test(lambda u: u.is_superuser)
def disable_user(request):
    user = request.user
    
    if request.method == 'GET':
        user = get_object_or_404(User, id = int(request.GET.get('userid')))
        if not user.get_profile().is_account_owner:
            user.is_active = False
            user.save()        
            request.user.message_set.create(message=_("User %s has been disable."%usernamegen(user) ))
        
    return HttpResponseRedirect(urlresolvers.reverse('rancho.user.views.all_people'))

@login_required
@user_passes_test(lambda u: u.is_superuser)
def enable_user(request):
    user = request.user
    
    if request.method == 'GET':
        user = get_object_or_404(User, id = int(request.GET.get('userid')))
        if not user.get_profile().is_account_owner:
            user.is_active = True
            user.save()         
            request.user.message_set.create(message=_("User %s has been enabled."%usernamegen(user) ))
        
    return HttpResponseRedirect(urlresolvers.reverse('rancho.user.views.all_people'))


@login_required
@user_passes_test(lambda u: u.is_superuser)
def view_user(request, user_id):
    me = request.user
    user = get_object_or_404(User, id = user_id)
    
    userprojects = Project.objects.get_projects_for_user(user)
        
    context = {'view_user': user, 'projects': userprojects}
    return render_to_response('people/view_user.html', 
                              context,
                              context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.is_superuser)
def newuser(request):
    """
    Adds a new user to the system
    """
    if request.method=='POST':    
        form = NewUserForm(request.POST)
        if form.is_valid():            
            newuser, newpassword, personal_note = form.save()        
                        
            #TODO: ROCHA: style this        
            context = {
                       'username': usernamegen(newuser, 'username'),
                       'fullname': usernamegen(newuser, 'fullname'),
                       'password': newpassword,
                       'site_name': "http://%s"%Site.objects.current_site.domain,                       
                       'link_login': "http://%s%s" % ( unicode(Site.objects.get_current()), urlresolvers.reverse('rancho.user.views.dashboard'),),
                       'link_pass': "http://%s%s" % ( unicode(Site.objects.get_current()), urlresolvers.reverse('rancho.user.views.edituser', args=[newuser.id]),),
                       'personal_note': personal_note
                       }
            content = render_to_string('emails/newuser.txt',context)            
            replyemail = 'no-reply@%s'%Site.objects.current_site.domain
            send_mail(_('New Rancho Register'), content, replyemail, [newuser.email])    
            
            request.user.message_set.create(message=_("User has been successfully created."))
            return HttpResponseRedirect(urlresolvers.reverse('rancho.user.views.all_people'))
        
    else:             
        form = NewUserForm(initial={'language': settings.LANGUAGE_CODE} )
        
    
    return render_to_response('people/add_user.html', 
                                {'newUserForm' : form},
                                context_instance=RequestContext(request))
        
    
@login_required
def edituser(request, user_id):
        
    user = request.user
    edit_user = get_object_or_404(User, id = user_id)
    edit_user_profile = edit_user.get_profile()
    context = {'edit_user': edit_user, 'edit_user_profile': edit_user_profile}

    if not can_edit_user(user, edit_user):    
        raise Http404('No %s matches the given query.'%user._meta.object_name)
    
    if user == edit_user:
        context['headermsg'] = _('Choose the email to which you will receive every notification from Rancho.')
    else:
        context['headermsg'] = _('Choose this person\'s email to which they will receive every notification from Rancho.')            
         
    if request.method == 'POST':
        data = request.POST.copy()
        data.update({u'username':edit_user.username})
        editUserForm = EditUserForm(data, request.FILES)
             
        if editUserForm.is_valid():
            editUserForm.save( edit_user, edit_user_profile)
             
            if edit_user == user:
                msg = _('Your settings have been successfully edited.')
            else:
                msg = _('The settings for %s have been successfully edited.'%edit_user.email)  
            request.user.message_set.create(message=msg)

    else:
        data = {'email': edit_user.email, 'first_name': edit_user.first_name, 'last_name': edit_user.last_name,
        'role': edit_user.is_superuser,
        'title': edit_user.get_profile().title, 'company': edit_user.get_profile().company.id, 
        'language': edit_user.get_profile().language , 'office': edit_user.get_profile().office, 
        'office_phone': edit_user.get_profile().office_phone, 'timezone': edit_user.get_profile().timezone,
        'office_phone_ext': edit_user.get_profile().office_phone_ext, 
        'mobile_phone': edit_user.get_profile().mobile_phone, 
        'home_phone': edit_user.get_profile().home_phone, 'im_name': edit_user.get_profile().im_name, 
        'im_service': edit_user.get_profile().im_service, 
        'mailing_address': edit_user.get_profile().mailing_address, 'webpage': edit_user.get_profile().webpage
        }
        editUserForm = EditUserForm(data)
         
    context['editUserForm'] = editUserForm
    return render_to_response('people/edit_user.html', 
                              context,
                              context_instance=RequestContext(request))

            
            
@login_required
@user_passes_test(lambda u: u.is_superuser)
def all_people(request):
    companies = Company.objects.all().order_by('-main_company', 'short_name')
    inactivepeople = User.objects.filter(is_active=False).order_by('userprofile__company')
        
    return render_to_response('people/view_people.html', 
                              {'companies': companies,
                               'inactivepeople': inactivepeople,
                               },
                              context_instance=RequestContext(request))

@login_required
def delete_small_photo(request, user_id):    
    user = request.user    
    edit_user = get_object_or_404(User, id=user_id)
    
    if not can_edit_user(user, edit_user):
        raise Http404('No %s matches the given query.'%user._meta.object_name)
     
    edit_user_profile = edit_user.get_profile()        
    if edit_user_profile.small_photo:
        edit_user_profile.small_photo.delete(save=False)
        edit_user_profile.small_photo = None        
        edit_user_profile.save()
        
    return HttpResponse('')
                
    
            
@login_required
def delete_large_photo(request, user_id):
    user = request.user    
    edit_user = get_object_or_404(User, id=user_id)
    
    if not can_edit_user(user, edit_user):
        raise Http404('No %s matches the given query.'%user._meta.object_name)
     
    edit_user_profile = edit_user.get_profile()        
    if edit_user_profile.large_photo:
        edit_user_profile.large_photo.delete(save=False)
        edit_user_profile.large_photo = None        
        edit_user_profile.save()
        
    return HttpResponse('')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def deleteUser(request, user_id):
        
    delete_user = get_object_or_404(User, id=user_id) 
    delete_user.state = 'D'
    delete_user.save()
    
    result = """<taconite>
    <eval>
        $("#userInfo{{user_id}}").fadeOut('slow');
    </eval>
    </taconite>
    """
    
    result = loader.get_template_from_string(result).render(Context({'user_id':user_id}))
    return HttpResponse(result, mimetype='text/xml')

@login_required
def change_language(request):
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'    

    if request.method == 'POST':
        lang_code = request.POST.get('language', None)
        if lang_code:
            user_profile = request.user.get_profile()
            user_profile.language = lang_code
            user_profile.save()
    return HttpResponseRedirect(next)

#########################################################
## help funtions


def can_edit_user(user, edit_user):
    
    if (user != edit_user and (not user.is_superuser)) or \
       (edit_user.get_profile().is_account_owner and (user != edit_user) )   :
        return False
    else:
        return True
