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
from django.utils.translation import ugettext_lazy as _
from rancho.chat.models import Post
import datetime



class ChatForm(forms.Form):

    message = forms.CharField(label = _('Message'), widget=forms.Textarea(attrs={'class':'fillx', 'rows': 2, 'id': 'message'}), error_messages={'required': _('The message cannot be blank.')})
    
    def __init__(self, request = None, *args, **kwargs):
        super(ChatForm, self).__init__(request,*args, **kwargs)
        
    def save(self, user, project, message = None):
        post = Post(
            date   = datetime.now(),
            message = message,
            author = user,
            project = project,
            )
        post.save()
        return post


class LogForm(forms.Form):

    from_date = forms.DateField(label=_('From date'), error_messages={'invalid':_('Invalid date format')}, required = False)
    to_date = forms.DateField(label=_('To date'), error_messages={'invalid':_('Invalid date format')}, required = False)
