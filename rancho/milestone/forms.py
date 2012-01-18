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
from django.forms.widgets import Select
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rancho.milestone.models import Milestone



class NewMilestoneForm(forms.Form):
    title = forms.CharField(label=_('Title'), widget=forms.TextInput(attrs={'class':'fillx'}), max_length=50,error_messages={'required': _('Please write a title for the milestone')})
    responsible = forms.ChoiceField(label=_('Responsible'))
    send_notification_email = forms.BooleanField(label=_('Send notification email'), required=False, initial=True)
    due_date = forms.DateField(label=_('Due date'), error_messages={'required': _('Due date field is empty'),'invalid':_('Invalid date format')})

    def __init__(self, users, request = None, *args, **kwargs):
        super(NewMilestoneForm, self).__init__(request,*args, **kwargs)
        self.fields['responsible'] = forms.ChoiceField(widget = Select, choices = users,
                                                       error_messages={'required' : _('Please select a responsible for the milestone'), 'invalid_choice' : _('invalid choice')})
    def save(self, user, project):
        milestone = Milestone()
        milestone.creator = user
        milestone.project = project
        user_id = int(self.cleaned_data['responsible'])
        if user_id != 0:
            milestone.responsible = get_object_or_404(User, id = user_id)
        milestone.title = self.cleaned_data['title']
        milestone.due_date = self.cleaned_data['due_date']
        milestone.send_notification_email = self.cleaned_data['send_notification_email']
        milestone.save()
        return milestone



