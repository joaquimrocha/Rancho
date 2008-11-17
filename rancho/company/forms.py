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

from rancho import settings



class CreateCompanyForm(forms.Form):
    short_name = forms.CharField(error_messages={'required': _("Please write a short name for the company")},
                                 max_length=10,label=_('Short Name'))
    long_name = forms.CharField(error_messages={'required': _("Please write a long name for the company")},
                                 max_length=100, widget=forms.TextInput(attrs={'size':40}),label=_('Long Name'))

class EditCompanySettingsForm(CreateCompanyForm):
    
        
    description = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'class':'fillx', 'rows': '5'}), label=_('Company Description'), required=False)
    
    mailing_address = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'cols':'55','rows': '3'}),label=_('Mailing Address'),required=False)
    
    phone = forms.CharField(max_length=20,widget=forms.TextInput(attrs={'size':'30'}),label=_('Phone'),required=False)
    
    webpage = forms.URLField(error_messages={'invalid': _("Please insert a valid webpage")},widget=forms.TextInput(attrs={'size':'30'}),label=_('Web Page'), required=False)
    
    logo = forms.ImageField(label=_('Company Logo'),widget=forms.FileInput(attrs={'size': 30}), required=False, error_messages={'invalid': _('The file you uploaded was either not an image or a corrupted image. Please choose a valid image file.')})
    
    display_logo_name = forms.BooleanField(required=False,label=_('Display company logo'))

    
    def __init__(self, request=None, *args, **kwargs):
        super(EditCompanySettingsForm, self).__init__(request,*args, **kwargs)
        
    def clean_logo(self):
        if self.files.has_key('logo'):
            if self.files.get('logo').size > settings.PROJECT_PIC_MAX_SIZE:
                raise forms.ValidationError(_('The image file you tried to upload is too large. Please upload an image of less than 1 Mb.'))
        return self.cleaned_data.get('logo')
        
