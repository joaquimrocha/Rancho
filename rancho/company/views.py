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
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from rancho import settings
from rancho.company.forms import CreateCompanyForm, ExportAccountForm, \
    ImportAccountForm, EditCompanySettingsForm
from rancho.company.models import Company, EventsHistory
from rancho.lib import serializer, utils
from rancho.project.models import Project
from rancho.user.views import can_see_user
from rancho.user.models import UserProfile

@login_required
@user_passes_test(lambda u: u.is_superuser)
def company_settings(request):

    user = request.user
    projects = Project.objects.get_projects_for_user(user)

    company = Company.objects.get(main_company=True)

    if request.method=='POST':

        editCompanySettingsForm = EditCompanySettingsForm(request.POST,request.FILES)

        if editCompanySettingsForm.is_valid():

            company.short_name = editCompanySettingsForm.cleaned_data['short_name']
            company.long_name = editCompanySettingsForm.cleaned_data['long_name']
            company.description = editCompanySettingsForm.cleaned_data['description']
            company.mailing_address = editCompanySettingsForm.cleaned_data['mailing_address']
            company.phone = editCompanySettingsForm.cleaned_data['phone']
            company.webpage = editCompanySettingsForm.cleaned_data['webpage']
            company.display_logo_name = editCompanySettingsForm.cleaned_data['display_logo_name']
            logo = editCompanySettingsForm.cleaned_data['logo']
            if logo:
                utils.save_image(company, company.id, logo, settings.COMPANY_LOGO_SIZE, 'logo', 'JPEG')

            company.save()

            request.user.message_set.create(message=_("Company settings have been successfully edited."))
    else :
        data = {'short_name':company.short_name,
               'long_name':company.long_name,
               'description':company.description,
               'mailing_address':company.mailing_address,
               'phone':company.phone,
               'webpage':company.webpage,
               'display_logo_name':company.display_logo_name,
               'logo':company.logo}
        editCompanySettingsForm = EditCompanySettingsForm(data)

    context = {'edit_company': company,
                'projects': projects,
                'editCompanySettingsForm': editCompanySettingsForm,
                'is_main_company': True
                }

    return render_to_response("company/settings.html", context,
                              context_instance = RequestContext(request))


@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_logo(request, c_id=None):
    if c_id:
        company = get_object_or_404(Company, id=c_id)
    else:
        company = Company.objects.get(main_company=True)

    if company.logo:
        company.logo.delete(save=False)
        company.logo = None
        company.save()

    return HttpResponse('')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_company(request):

    if request.method == 'POST':
        form = CreateCompanyForm(request.POST)
        if form.is_valid():
            new_company = Company()
            new_company.short_name = form.cleaned_data['short_name']
            new_company.long_name = form.cleaned_data['long_name']
            new_company.save()

            request.user.message_set.create(message=_("Company %s have been successfully created."%new_company.short_name))
            return HttpResponseRedirect(urlresolvers.reverse('rancho.user.views.all_people'))
    else:
        form = CreateCompanyForm()

    return render_to_response("company/create.html",
                              {'form': form},
                              context_instance = RequestContext(request))


@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_company(request, c_id):
    user = request.user
    company = get_object_or_404(Company, id=c_id)

    if company.main_company and user.get_profile().is_account_owner:
        return HttpResponseRedirect(urlresolvers.reverse('rancho.company.views.company_settings'))
    elif company.main_company:
        return HttpResponseRedirect(urlresolvers.reverse('rancho.user.views.all_people'))

    if request.method == 'POST':
        form = CreateCompanyForm(request.POST)
        if form.is_valid():
            company.short_name = form.cleaned_data['short_name']
            company.long_name = form.cleaned_data['long_name']
            company.save()

            request.user.message_set.create(message=_("Company %s information has been successfully updated."%company.short_name))
            return HttpResponseRedirect(urlresolvers.reverse('rancho.user.views.all_people'))
    else:
        data = {'short_name': company.short_name,
                'long_name': company.long_name,
                }
        form = CreateCompanyForm(data)

    return render_to_response("company/edit.html",
                              {'form': form,
                               'editcompany': company},
                              context_instance = RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_company(request):

    if request.method == 'GET':
        company = get_object_or_404(Company, id = int(request.GET.get('c_id')))

        if company.main_company:
            return HttpResponseRedirect(urlresolvers.reverse('rancho.user.views.all_people'))
        else:
            main_company = Company.objects.get(main_company=True)
            if company.userprofile_set.count() > 0:
                company.userprofile_set.update(company=main_company)
                company.delete()
            else:
                company.delete()
            request.user.message_set.create(message=_("Company %s has been deleted."%company.short_name))

    return HttpResponseRedirect(urlresolvers.reverse('rancho.user.views.all_people'))

@login_required
def view_company(request, company_id):

    user = request.user
    company = get_object_or_404(Company, id = company_id)

    if not can_see_company(user, company):
        raise Http404()

    return render_to_response("company/view.html",
                              {'c': company},
                              context_instance = RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_superuser)
def show_logs(request):

    ev = EventsHistory.objects.all().order_by('-date')

    return render_to_response("company/show_logs.html",
                              {'events': ev},
                              context_instance = RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_superuser)
def download_logs(request):
    import cStringIO
    output = cStringIO.StringIO()
    output.write('"Date";"Action";"Type";"Title";"Project";"Link"\n')
    for e in EventsHistory.objects.all().order_by('-date'):
        if e.content_type and e.content_type.name != "project" and hasattr(e.content_type, "project"):
            project = e.content_object.project
        else:
            project = ""

        if e.content_object and hasattr(e.content_object, "get_absolute_url"):
            url = "http://%s%s"%(Site.objects.get_current(),e.content_object.get_absolute_url())
        else:
            url = ""

        str = '"%s";"%s";"%s";"%s";"%s";"%s"\n'%\
            (e.date, e.get_type_display(), e.content_type, e.title, project, url)
        output.write(smart_str(str))

    output.seek(0)
    response = HttpResponse(output)
    response['Content-Type'] = 'text/comma-separated-values'
    response['Content-Disposition'] = 'attachment; filename="history.csv"'
    return response

@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_account(request):

    user = request.user
    company = Company.objects.get(main_company=True)

    if request.method == 'POST':
        form = ExportAccountForm(request.POST)
        if form.is_valid():
            return serializer.export_account(user.get_profile().company.short_name, form.cleaned_data['components'])
    else:
        form = ExportAccountForm()

    return render_to_response("company/export.html",
                              {'form': form,
                               'company': company},
                                context_instance = RequestContext(request))

@login_required
@transaction.commit_manually
@user_passes_test(lambda u: u.is_superuser)
def import_account(request):

    user = request.user
    company = Company.objects.get(main_company=True)

    if request.method == 'POST':
        form = ImportAccountForm(request.POST, request.FILES)
        if form.is_valid():
            system = None
            if form.cleaned_data['importation_type'] == 'B':
                system = 'BASECAMP'
            try:
                serializer.import_account(form.cleaned_data['importation_file'], system)
            except:
                import traceback
                transaction.rollback()
                traceback.print_exc()
                request.user.message_set.create(message = _('Error performing importation'))
            else:
                transaction.commit()
                request.user.message_set.create(message = _('Importation successful'))
                return HttpResponseRedirect(urlresolvers.reverse('rancho.user.views.dashboard'))
    else:
        form = ImportAccountForm()

    return render_to_response("company/import.html",
                              {'form': form,
                               'company': company},
                              context_instance = RequestContext(request))

def can_see_company(user, company):

    users_in_company = [profile.user for profile in \
                        UserProfile.objects.filter(company = company)]
    if user in users_in_company:
        return True
    for user_in_company in users_in_company:
        if can_see_user(user, user_in_company):
            return True
    return False
