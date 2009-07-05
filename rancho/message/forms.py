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
from rancho.lib.custom_widgets import AjaxTags, \
    ShowAndSelectMultipleNotification
from rancho.message.models import Message
from rancho.tagging.forms import TagField
import datetime



class MessageForm(forms.Form):
    
    title=forms.CharField(label=_('Title'), widget=forms.TextInput(attrs={'class':'fillx'}), max_length=50,error_messages={'required': _('Please write a title for the message')})
    tags=TagField(label = _('Tags'), required=False)    
    message=forms.CharField(label=_('Body'), widget=forms.Textarea(attrs={'class':'fillx'}), error_messages={'required': _('The message body cannot be blank.')})
    notify=forms.MultipleChoiceField(label=_('Notify'))
    
    def __init__(self,list_users, tagslist, request=None, *args, **kwargs):
        super(MessageForm, self).__init__(request,*args, **kwargs)
        
        list = [(user.id, user) for user in list_users]        
        self.fields['notify']=forms.MultipleChoiceField(widget=ShowAndSelectMultipleNotification,required=False, choices=list)
        
        #self.fields['notify']=forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,required=False, choices=list_users)            
        self.fields['tags'].widget=AjaxTags(tagslist, attrs={'class':'fillx'})
        
    def save(self, user, project, message=None):
        if message: #update
            message.title   = self.cleaned_data['title']
            message.body   = self.cleaned_data['message']
            message.tags = self.cleaned_data['tags']            
            message.save()
            return message
        else: #new
            me=Message(
                title   = self.cleaned_data['title'],
                body    = self.cleaned_data['message'],
                tags = self.cleaned_data['tags'],
                creator  = user,
                project = project,
            )                    
            me.save()            
            [me.notify_to.add(user) for user in self.cleaned_data['notify']]
            me.initial_message=me
            me.save()
            me.read_by.add(user)
            return me
                
class CommentForm(forms.Form):
    message=forms.CharField(label=_('Body'), widget=forms.Textarea(attrs={'class':'fillx'}),error_messages={'required': _('Please write a message')})
    
    def save(self, user, project, message, new=False):
        if new:
            me=Message(
               title   = message.title,
               body    = self.cleaned_data['message'],
               creator  = user,
               project = project,
               initial_message = message,
            )
            me.save()
            return me
        else:
            message.body    = self.cleaned_data['message']
            message.creation_date = datetime.datetime.now()
            message.save()
            return message
