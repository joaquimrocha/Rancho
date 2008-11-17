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
from django.utils.translation import ugettext as _

from rancho.wikiboard.models import Wiki
from rancho.tinymce.widgets import TinyMCE

class TinyMceForm(forms.Form):
    mceconf = {'theme':'advanced', 
               'theme_advanced_toolbar_location': 'top',
               'theme_advanced_toolbar_align': 'left',
               'theme_advanced_buttons1': 'fullscreen,separator,preview,separator,bold,italic,underline,strikethrough,separator,bullist,numlist,outdent,indent,separator,undo,redo,fontsizeselect,forecolor,separator,link,unlink,anchor,separator,image',
               'theme_advanced_buttons2': '',
               'theme_advanced_buttons3': '',
               'plugins': 'fullscreen,preview',               
               }        
    content = forms.CharField(label='', widget=TinyMCE(attrs={'class': 'fillx', 'rows': 30},mce_attrs=mceconf), required=False)

class NewWikiEntryForm(TinyMceForm):    
    wiki_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':40,'class': 'big_entry'}),label=_("Wiki Name"))
    
    def clean_wiki_name(self, *args, **kwargs):
        wiki = Wiki.objects.filter(name=self.cleaned_data['wiki_name'] )            
        if wiki :
            raise forms.ValidationError(_("Wiki name already exist, please choose other."))        
        return self.cleaned_data['wiki_name']        
    
    

    
