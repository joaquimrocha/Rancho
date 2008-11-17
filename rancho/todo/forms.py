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
from django.utils.translation import ugettext_lazy as _


class NewToDoListForm(forms.Form):
    
    todolist_name = forms.CharField(widget=forms.TextInput(attrs={'size':40, 'class': 'big_entry'}),label=_("Name"))
    todolist_description = forms.CharField(widget=forms.Textarea(attrs={'class': 'fillx', 'rows':4}), required=False,label=_("Description"))

class EditToDoListForm(NewToDoListForm):
    pass

class EditToDoForm(forms.Form):
    title = forms.CharField(label=_('Title'), widget=forms.TextInput(attrs={'class':'fillx'}), max_length=50,error_messages={'required': _('Please write a title for the ToDo item')})
    responsible = forms.ChoiceField(label=_('Responsible'))
    
    def __init__(self, users, request = None, *args, **kwargs):
        super(EditToDoForm, self).__init__(request,*args, **kwargs)
        self.fields['responsible'] = forms.ChoiceField(widget = Select, choices = users,
                                                       error_messages={'required' : _('Please select a responsible for the ToDo item'), 'invalid_choice' : _('invalid choice')})
