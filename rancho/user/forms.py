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
from django.forms.widgets import RadioSelect
from django.contrib.auth.models import User

from rancho.user.models import UserProfile
from rancho.company.models import Company
from rancho.lib import utils
from rancho.timezones.forms import TimeZoneField
from rancho.lib.custom_widgets import MyRadioFieldRenderer

from rancho import settings

def company_choices( ):
    companies = [(c.id, c.short_name) for c in Company.objects.all()]
    return tuple(companies)
        
        
class UserForm(forms.Form):
    YES_NO_CHOICES = ((True, _('Yes')),
                      (False, _('No')),
                      )
    
    email = forms.EmailField(error_messages={'required': _('The user email cannot be empty.'), 'invalid': _('Please insert a valid email.')},widget=forms.TextInput(attrs={'class':'large'}),label=_("E-Mail"))
    company = forms.ChoiceField(choices=company_choices(), label=_('Company'))
    language = forms.ChoiceField(choices=settings.LANGUAGES, label=_('Language'))
    role = forms.ChoiceField(required=False, widget=RadioSelect(renderer=MyRadioFieldRenderer), choices=YES_NO_CHOICES, label=_('Is Admin'), initial=False)
    timezone = TimeZoneField(label=_('Timezone'), initial=settings.TIME_ZONE)
    
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'large'}),label=_("First Name"))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'large'}), label=_("Last Name"))
    title = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'large'}),label=_("Title"))

    office = forms.CharField(required=False,label=_("Office"))    
    office_phone = forms.CharField(required=False,label=_("Office Phone"))
    office_phone_ext = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'small'}), label="Office Phone Ext ")
    mobile_phone = forms.CharField(required=False, label=_("Mobile Phone"))
    home_phone = forms.CharField(required=False, label=_("Home Phone"))
    
    im_name = forms.CharField(required=False,label=_("IM Name"))
    im_service = forms.ChoiceField(required=False, choices=UserProfile.IM_SERVICES_CHOICES,label=_("IM Service"))
    mailing_address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'small'}),label=_("Mailing Address"))
    webpage = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'large'}),label=_("Webpage"))
    
    personal_note = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'small_wide'}),label=_("Personal Note"))

    
class NewUserForm(UserForm):
    
    username = forms.CharField(error_messages={'required': _('The username cannot be empty.')}, widget=forms.TextInput(attrs={'class':'large'}), label=_("Username"))
        
    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
                        
        self.fields['company'].choices = company_choices()
        
    def clean_username(self):        
        try:
            user = User.objects.get(username=self.data['username'])
            raise forms.ValidationError(_('There is already a user with the username you inserted, please choose another username.'))
        except User.DoesNotExist:
            return self.cleaned_data.get('username')
     
    def clean_email(self):        
        try:
            user = User.objects.get(email__iexact=self.data['email'])
            raise forms.ValidationError(_('There is already a user with the email you inserted, please choose another email.'))
        except User.DoesNotExist:
            return self.cleaned_data.get('email')
    
    
    def save(self):
        user = User()  
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.is_superuser = (self.cleaned_data['role'] == 'True')
        user.is_active = True            
        user.save()
        
        user_profile = UserProfile()
        user_profile.user = user            
        user_profile.title = self.cleaned_data['title']
        user_profile.company_id = self.cleaned_data['company']
        user_profile.language = self.cleaned_data['language']        
        user_profile.timezone = self.cleaned_data['timezone']
        user_profile.office = self.cleaned_data['office']
        user_profile.office_phone = self.cleaned_data['office_phone']
        user_profile.office_phone_ext = self.cleaned_data['office_phone_ext']
        user_profile.mobile_phone = self.cleaned_data['mobile_phone']
        user_profile.home_phone = self.cleaned_data['home_phone']
        user_profile.im_name = self.cleaned_data['im_name']
        user_profile.im_service = self.cleaned_data['im_service']
        user_profile.mailing_address = self.cleaned_data['mailing_address']
        user_profile.webpage = self.cleaned_data['webpage']
        user_profile.external_login=0
        user_profile.save()
        
        password = utils.gen_random_pass()
        user.set_password(password)
        user.save()
        
        return user, password, self.cleaned_data['personal_note']
        
    
class EditUserForm(UserForm):
        
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(label=_("New password confirmation"), widget=forms.PasswordInput, required=False)
    
    small_photo = forms.ImageField(label=_('Small Photo'), widget=forms.FileInput(attrs={'size':30, 'class': 'project_upload_photo'}), required=False, error_messages={'invalid': _('The file you uploaded was either not an image or a corrupted image. Please choose a valid image file.')})
    large_photo = forms.ImageField(label=_('Large Photo'), widget=forms.FileInput(attrs={'size':30, 'class': 'project_upload_photo'}), required=False, error_messages={'invalid': _('The file you uploaded was either not an image or a corrupted image. Please choose a valid image file.')})
    
    def __init__(self, edit_user, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
                        
        self.edit_user = edit_user
    
    def clean_small_photo(self):
        if self.files.has_key('small_photo'):
            if self.files.get('small_photo').size > settings.PROJECT_PIC_MAX_SIZE:
                raise forms.ValidationError(_('The image file you tried to upload is too large. Please upload an image of less than 1 Mb.'))

        return self.cleaned_data.get('small_photo')
    
    def clean_large_photo(self):
        if self.files.has_key('large_photo'):            
            if self.files.get('large_photo').size > settings.PROJECT_PIC_MAX_SIZE:
                raise forms.ValidationError(_('The image file you tried to upload is too large. Please upload an image of less than 1 Mb.'))

        return self.cleaned_data.get('large_photo')
    
    def clean_new_password2(self):
        password1 = self.cleaned_data['new_password1']
        password2 = self.cleaned_data['new_password2']
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return password2
    
    def clean_email(self):        
        try:
            user = User.objects.get(email=self.data['email'])
            if user != self.edit_user:
                raise forms.ValidationError(_('There is already a user with the email you inserted, please choose another email.'))
        except User.DoesNotExist:
            pass
        
        return self.cleaned_data.get('email')
    
    def save(self, edit_user, edit_user_profile):
                        
        edit_user.email = self.cleaned_data['email']
        edit_user.first_name = self.cleaned_data['first_name']
        edit_user.last_name = self.cleaned_data['last_name']
        if self.cleaned_data['role']:            
            edit_user.is_superuser = (self.cleaned_data['role'] == 'True')
        if self.cleaned_data['new_password1']:
            edit_user.set_password(self.cleaned_data['new_password1'])        
        edit_user.save()        
        
        edit_user_profile.title = self.cleaned_data['title']
        edit_user_profile.company_id = self.cleaned_data['company']
        edit_user_profile.language = self.cleaned_data['language']
        edit_user_profile.timezone = self.cleaned_data['timezone']
        edit_user_profile.office = self.cleaned_data['office']
        edit_user_profile.office_phone = self.cleaned_data['office_phone']
        edit_user_profile.office_phone_ext = self.cleaned_data['office_phone_ext']
        edit_user_profile.mobile_phone = self.cleaned_data['mobile_phone']
        edit_user_profile.home_phone = self.cleaned_data['home_phone']
        edit_user_profile.im_name = self.cleaned_data['im_name']
        edit_user_profile.im_service = self.cleaned_data['im_service']
        edit_user_profile.mailing_address = self.cleaned_data['mailing_address']
        edit_user_profile.webpage = self.cleaned_data['webpage']
        
        if self.cleaned_data['small_photo']:
            utils.save_image(edit_user_profile, edit_user.id, self.cleaned_data['small_photo'], settings.PROFILE_PICTURE_SIZE, 'small_photo')
        
        if self.cleaned_data['large_photo']:
            utils.save_image(edit_user_profile, '%s_large' % edit_user.id, self.cleaned_data['large_photo'], settings.PROFILE_LARGE_PICTURE_SIZE, 'large_photo')
            
        edit_user_profile.save()
            
            
    
