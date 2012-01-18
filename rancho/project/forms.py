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

from django import forms
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rancho import settings
from rancho.company.models import Company
from rancho.granular_permissions.permissions import PERMISSIONS_TODO_EDITDELETE, \
    PERMISSIONS_TODO_CREATE, PERMISSIONS_TODO_VIEW, PERMISSIONS_MILESTONE_EDITDELETE, \
    PERMISSIONS_MILESTONE_CREATE, PERMISSIONS_MILESTONE_VIEW, \
    PERMISSIONS_WIKIBOARD_EDITDELETE, PERMISSIONS_WIKIBOARD_CREATE, \
    PERMISSIONS_WIKIBOARD_VIEW, PERMISSIONS_FILE_EDITDELETE, PERMISSIONS_FILE_CREATE, \
    PERMISSIONS_FILE_VIEW, PERMISSIONS_MESSAGE_EDITDELETE, \
    PERMISSIONS_MESSAGE_CREATE, PERMISSIONS_MESSAGE_VIEW
from rancho.lib import utils
from rancho.lib.custom_widgets import ShowAndSelectMultipleProject, \
    PermissionsField, MyRadioFieldRenderer
from rancho.project.models import Project, UserInProject



class NewProjectForm(forms.Form):
    project_name = forms.CharField(label=_('Name'), widget=forms.TextInput(attrs={'size':40, 'class': 'big_entry'}))
    project_logo = forms.ImageField(label=_('Logo'),widget=forms.FileInput(attrs={'size':30, 'class': 'project_upload_photo'}), required=False, error_messages={'invalid': _('The file you uploaded was either not an image or a corrupted image. Please choose a valid image file.')})

    def clean_project_name(self):
        if Project.objects.filter(name=self.cleaned_data['project_name']):
            raise forms.ValidationError(_('This project name is already in use.'))
        return self.cleaned_data['project_name']

    def clean_project_logo(self):
        if self.files.has_key('project_logo'):
            if self.files.get('project_logo').size > settings.PROJECT_PIC_MAX_SIZE:
                raise forms.ValidationError(_('The image file you tried to upload is too large. Please upload an image of less than 1 Mb.'))
        return self.cleaned_data.get('project_logo')

    def save(self, user):
        project = Project()
        project.name = self.cleaned_data['project_name']
        project.status = 'A'
        project.creator = user
        project.company = Company.objects.get(main_company = True)
        project.save()
        logo = self.cleaned_data['project_logo']
        if logo != None:
            utils.save_image(project, project.id, logo, settings.PROJECT_LOGO_SIZE, 'logo', 'JPEG')
        project.save()

        user_in_p = UserInProject(
                                  user=user,
                                  project=project,
                                  state='a',
                    )
        user_in_p.save()

        return project


class EditProjectSettingsForm(NewProjectForm):
    project_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'large'}), label=_('Name'))
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'fillx', 'rows': '5'}), label=_('Project Description'), required=False)
    status = forms.ChoiceField(widget=forms.RadioSelect(renderer=MyRadioFieldRenderer), choices=Project.PROJECT_STATUS_CHOICES, label=_('Project Status'))

    def __init__(self, project, request=None, *args, **kwargs):
        self.project = project
        super(EditProjectSettingsForm, self).__init__(request,*args, **kwargs)

    def clean_project_name(self):
        p = Project.objects.filter(name=self.cleaned_data['project_name'])
        if p and p[0] != self.project:
            raise forms.ValidationError(_('This project name is already in use.'))
        return self.cleaned_data['project_name']

    def save(self, project):
        project.name = self.cleaned_data['project_name']
        project.status = self.cleaned_data['status']
        project.description = self.cleaned_data['description']
        logo = self.cleaned_data['project_logo']
        project.save()
        if logo != None:
            utils.save_image(project, project.id, logo, settings.PROJECT_LOGO_SIZE, 'logo', 'JPEG')


class AddPeopleForm(forms.Form):

    permissions = PermissionsField( required=False)


    def __init__(self, users_list,request=None, *args, **kwargs):
        super(AddPeopleForm, self).__init__(request,*args, **kwargs)
        #transform the list so the widget can use it
        list = [(user.id, user) for user in users_list]
        self.fields['user_not_in_project']=forms.MultipleChoiceField(widget=ShowAndSelectMultipleProject,required=False, choices=list)


    def save(self, project):

        for uid in self.cleaned_data['user_not_in_project']:
            user = get_object_or_404(User, id=uid)

            up = UserInProject()
            up.user = user
            up.project = project
            up.state = 'a'
            up.save()
            formperm = self.cleaned_data['permissions']

            if formperm['message'] == 'delete':
                user.add_row_perm(project, PERMISSIONS_MESSAGE_EDITDELETE)
                user.add_row_perm(project, PERMISSIONS_MESSAGE_CREATE)
                user.add_row_perm(project, PERMISSIONS_MESSAGE_VIEW)
            elif formperm['message'] == 'create':
                user.add_row_perm(project, PERMISSIONS_MESSAGE_CREATE)
                user.add_row_perm(project, PERMISSIONS_MESSAGE_VIEW)
            elif formperm['message'] == 'view':
                user.add_row_perm(project, PERMISSIONS_MESSAGE_VIEW)

            if formperm['todo'] == 'delete':
                user.add_row_perm(project, PERMISSIONS_TODO_EDITDELETE)
                user.add_row_perm(project, PERMISSIONS_TODO_CREATE)
                user.add_row_perm(project, PERMISSIONS_TODO_VIEW)
            elif formperm['todo'] == 'create':
                user.add_row_perm(project, PERMISSIONS_TODO_CREATE)
                user.add_row_perm(project, PERMISSIONS_TODO_VIEW)
            elif formperm['todo'] == 'view':
                user.add_row_perm(project, PERMISSIONS_TODO_VIEW)

            if formperm['milestone'] == 'delete':
                user.add_row_perm(project, PERMISSIONS_MILESTONE_EDITDELETE)
                user.add_row_perm(project, PERMISSIONS_MILESTONE_CREATE)
                user.add_row_perm(project, PERMISSIONS_MILESTONE_VIEW)
            elif formperm['milestone'] == 'create':
                user.add_row_perm(project, PERMISSIONS_MILESTONE_CREATE)
                user.add_row_perm(project, PERMISSIONS_MILESTONE_VIEW)
            elif formperm['milestone'] == 'view':
                user.add_row_perm(project, PERMISSIONS_MILESTONE_VIEW)

            if formperm['wikiboard'] == 'delete':
                user.add_row_perm(project, PERMISSIONS_WIKIBOARD_EDITDELETE)
                user.add_row_perm(project, PERMISSIONS_WIKIBOARD_CREATE)
                user.add_row_perm(project, PERMISSIONS_WIKIBOARD_VIEW)
            elif formperm['wikiboard'] == 'create':
                user.add_row_perm(project, PERMISSIONS_WIKIBOARD_CREATE)
                user.add_row_perm(project, PERMISSIONS_WIKIBOARD_VIEW)
            elif formperm['wikiboard'] == 'view':
                user.add_row_perm(project, PERMISSIONS_WIKIBOARD_VIEW)

            if formperm['file'] == 'delete':
                user.add_row_perm(project, PERMISSIONS_FILE_EDITDELETE)
                user.add_row_perm(project, PERMISSIONS_FILE_CREATE)
                user.add_row_perm(project, PERMISSIONS_FILE_VIEW)
            elif formperm['file'] == 'create':
                user.add_row_perm(project, PERMISSIONS_FILE_CREATE)
                user.add_row_perm(project, PERMISSIONS_FILE_VIEW)
            elif formperm['file'] == 'view':
                user.add_row_perm(project, PERMISSIONS_FILE_VIEW)


class EditPermissionsForm(forms.Form):

    permissions = PermissionsField( required=False)

    def save(self, user, project):
        formperm = self.cleaned_data['permissions']

        if formperm['message'] == 'delete':
            user.add_row_perm(project, PERMISSIONS_MESSAGE_EDITDELETE)
            user.add_row_perm(project, PERMISSIONS_MESSAGE_CREATE)
            user.add_row_perm(project, PERMISSIONS_MESSAGE_VIEW)
        elif formperm['message'] == 'create':
            user.del_row_perm(project, PERMISSIONS_MESSAGE_EDITDELETE)
            user.add_row_perm(project, PERMISSIONS_MESSAGE_CREATE)
            user.add_row_perm(project, PERMISSIONS_MESSAGE_VIEW)
        elif formperm['message'] == 'view':
            user.del_row_perm(project, PERMISSIONS_MESSAGE_EDITDELETE)
            user.del_row_perm(project, PERMISSIONS_MESSAGE_CREATE)
            user.add_row_perm(project, PERMISSIONS_MESSAGE_VIEW)
        else:
            user.del_row_perm(project, PERMISSIONS_MESSAGE_EDITDELETE)
            user.del_row_perm(project, PERMISSIONS_MESSAGE_CREATE)
            user.del_row_perm(project, PERMISSIONS_MESSAGE_VIEW)

        if formperm['todo'] == 'delete':
            user.add_row_perm(project, PERMISSIONS_TODO_EDITDELETE)
            user.add_row_perm(project, PERMISSIONS_TODO_CREATE)
            user.add_row_perm(project, PERMISSIONS_TODO_VIEW)
        elif formperm['todo'] == 'create':
            user.del_row_perm(project, PERMISSIONS_TODO_EDITDELETE)
            user.add_row_perm(project, PERMISSIONS_TODO_CREATE)
            user.add_row_perm(project, PERMISSIONS_TODO_VIEW)
        elif formperm['todo'] == 'view':
            user.del_row_perm(project, PERMISSIONS_TODO_EDITDELETE)
            user.del_row_perm(project, PERMISSIONS_TODO_CREATE)
            user.add_row_perm(project, PERMISSIONS_TODO_VIEW)
        else:
            user.del_row_perm(project, PERMISSIONS_TODO_EDITDELETE)
            user.del_row_perm(project, PERMISSIONS_TODO_CREATE)
            user.del_row_perm(project, PERMISSIONS_TODO_VIEW)

        if formperm['milestone'] == 'delete':
            user.add_row_perm(project, PERMISSIONS_MILESTONE_EDITDELETE)
            user.add_row_perm(project, PERMISSIONS_MILESTONE_CREATE)
            user.add_row_perm(project, PERMISSIONS_MILESTONE_VIEW)
        elif formperm['milestone'] == 'create':
            user.del_row_perm(project, PERMISSIONS_MILESTONE_EDITDELETE)
            user.add_row_perm(project, PERMISSIONS_MILESTONE_CREATE)
            user.add_row_perm(project, PERMISSIONS_MILESTONE_VIEW)
        elif formperm['milestone'] == 'view':
            user.del_row_perm(project, PERMISSIONS_MILESTONE_EDITDELETE)
            user.del_row_perm(project, PERMISSIONS_MILESTONE_CREATE)
            user.add_row_perm(project, PERMISSIONS_MILESTONE_VIEW)
        else:
            user.del_row_perm(project, PERMISSIONS_MILESTONE_EDITDELETE)
            user.del_row_perm(project, PERMISSIONS_MILESTONE_CREATE)
            user.del_row_perm(project, PERMISSIONS_MILESTONE_VIEW)


        if formperm['wikiboard'] == 'delete':
            user.add_row_perm(project, PERMISSIONS_WIKIBOARD_EDITDELETE)
            user.add_row_perm(project, PERMISSIONS_WIKIBOARD_CREATE)
            user.add_row_perm(project, PERMISSIONS_WIKIBOARD_VIEW)
        elif formperm['wikiboard'] == 'create':
            user.del_row_perm(project, PERMISSIONS_WIKIBOARD_EDITDELETE)
            user.add_row_perm(project, PERMISSIONS_WIKIBOARD_CREATE)
            user.add_row_perm(project, PERMISSIONS_WIKIBOARD_VIEW)
        elif formperm['wikiboard'] == 'view':
            user.del_row_perm(project, PERMISSIONS_WIKIBOARD_EDITDELETE)
            user.del_row_perm(project, PERMISSIONS_WIKIBOARD_CREATE)
            user.add_row_perm(project, PERMISSIONS_WIKIBOARD_VIEW)
        else:
            user.del_row_perm(project, PERMISSIONS_WIKIBOARD_EDITDELETE)
            user.del_row_perm(project, PERMISSIONS_WIKIBOARD_CREATE)
            user.del_row_perm(project, PERMISSIONS_WIKIBOARD_VIEW)


        if formperm['file'] == 'delete':
            user.add_row_perm(project, PERMISSIONS_FILE_EDITDELETE)
            user.add_row_perm(project, PERMISSIONS_FILE_CREATE)
            user.add_row_perm(project, PERMISSIONS_FILE_VIEW)
        elif formperm['file'] == 'create':
            user.del_row_perm(project, PERMISSIONS_FILE_EDITDELETE)
            user.add_row_perm(project, PERMISSIONS_FILE_CREATE)
            user.add_row_perm(project, PERMISSIONS_FILE_VIEW)
        elif formperm['file'] == 'view':
            user.del_row_perm(project, PERMISSIONS_FILE_EDITDELETE)
            user.del_row_perm(project, PERMISSIONS_FILE_CREATE)
            user.add_row_perm(project, PERMISSIONS_FILE_VIEW)
        else:
            user.del_row_perm(project, PERMISSIONS_FILE_EDITDELETE)
            user.del_row_perm(project, PERMISSIONS_FILE_CREATE)
            user.del_row_perm(project, PERMISSIONS_FILE_VIEW)

