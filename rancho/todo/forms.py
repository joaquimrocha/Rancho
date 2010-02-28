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
from django.forms.widgets import Select
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rancho.milestone.models import Milestone
from rancho.todo.models import ToDoList

class NewToDoListForm(forms.Form):
    
    todolist_name = forms.CharField(widget=forms.TextInput(attrs={'size':40, 'class': 'big_entry'}), max_length = 50, label=_("Name"))
    todolist_description = forms.CharField(widget=forms.Textarea(attrs={'class': 'fillx', 'rows':4}), required=False,label=_("Description"))

    def __init__(self, milestones, *args, **kwargs):
        super(NewToDoListForm, self).__init__(*args, **kwargs)
        self.fields['milestone'] = forms.ChoiceField(widget = Select,
                                                     label = _('Milestone:'),
                                                     choices = milestones,
                                                     required = False)

    def save_with_form_data(self, todo_list):
        todo_list.title = self.cleaned_data['todolist_name']
        todo_list.description = self.cleaned_data['todolist_description']
        milestone_id = int(self.cleaned_data['milestone'] or 0)
        if milestone_id:
            milestone = get_object_or_404(Milestone, id = milestone_id)
        else:
            milestone = None
        todo_list.milestone = milestone
        todo_list.save()

    def save(self, creator, project):
        todo_list = ToDoList()
        todo_list.creator = creator
        todo_list.project = project
        self.save_with_form_data(todo_list)
        return todo_list

class EditToDoListForm(NewToDoListForm):
    pass

class EditToDoForm(forms.Form):
    title = forms.CharField(label=_('Title'), widget=forms.TextInput(attrs={'class':'fillx'}), max_length=50,error_messages={'required': _('Please write a title for the ToDo item')})
    responsible = forms.ChoiceField(label=_('Responsible'))
    
    def __init__(self, users, request = None, *args, **kwargs):
        super(EditToDoForm, self).__init__(request,*args, **kwargs)
        self.fields['responsible'] = forms.ChoiceField(widget = Select, choices = users,
                                                       error_messages={'required' : _('Please select a responsible for the ToDo item'), 'invalid_choice' : _('invalid choice')})
