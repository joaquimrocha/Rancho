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

from django.forms.widgets import chain, force_unicode, mark_safe
from django.forms.widgets import RadioFieldRenderer
from django.utils.translation import ugettext_lazy as _
from django.template import loader, Context
from django.forms.widgets import TextInput, Widget, Select, CheckboxInput, SelectMultiple
from django import forms

from rancho.granular_permissions import permissions

#TODO: Clean this
class ShowAndSelectMultipleBase(SelectMultiple):

    def render(self, name, value, attrs=None, choices=()):
        PERSON_COL=3
        tmpcol = 1
        old_group = None

        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<table width="100%">']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])

        for i, (option_value, user) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            rendered_cb = cb.render(name, force_unicode(option_value))

            #do group
            if old_group != user.get_profile().company:
                if tmpcol > 1 :
                    for i in range(tmpcol, PERSON_COL+1 ):
                        output.append( '<td></td>' )
                    output.append(u'</tr>')

                output.append(  u'<tr><td colspan="%(col)s"><p style="margin: 15px 0 10px 0;"><a class="smallcaps_title blue_bg white" href="">%(name)s</a></p></td></tr>'%{'col': PERSON_COL, 'name': user.get_profile().company.short_name} )
                tmpcol = 1
                old_group = user.get_profile().company
            #do user
            u = self.myrender(user, label_for, rendered_cb)
            if tmpcol == 1:
                u = '<tr>' + u
                tmpcol  += 1
            elif tmpcol == PERSON_COL:
                u += '</tr>'
                tmpcol = 1
            else:
                tmpcol  += 1
            output.append( u  )

        if tmpcol > 1 :
            for i in range(tmpcol, PERSON_COL+1 ):
                output.append( '<td></td>' )
            output.append(u'</tr>')
        output.append(u'</table>')

        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_
    id_for_label = classmethod(id_for_label)

class ShowAndSelectMultipleProject(ShowAndSelectMultipleBase):
    def myrender(self, user, label_for, rendered_cb):
        u = '''
            {%% load displayuser %%}
            <td>
            <div style="float: left; margin-top: 15px;">
            %(cb)s
            </div>
            {%% displayuser user %%}
            </td>
            ''' % {'name': user.get_full_name(), 'email': user.email,'lbl': label_for, 'cb': rendered_cb}
        context = Context()
        context['user'] = user
        return loader.get_template_from_string(u).render(context)

class ShowAndSelectMultipleNotification(ShowAndSelectMultipleBase):
    def myrender(self, user, label_for, rendered_cb):
        u = '''
            {%% load usernamegen %%}
            <td>
            %(cb)s <label%(lbl)s>{%% usernamegen user 'fullname' %%}</label>
            </td>
            ''' % {'lbl': label_for, 'cb': rendered_cb}
        context = Context()
        context['user'] = user
        return loader.get_template_from_string(u).render(context)


class AjaxTags(forms.TextInput):
    def __init__(self, available_tags, *args, **kwargs):
        self.available_tags = available_tags
        super(AjaxTags, self).__init__(*args, **kwargs)


    def render(self, name, value, attrs=None):
        textinput = super(TextInput, self).render(name, value, attrs)

        if self.available_tags:
            showmorestr = _('Show Tags')
            showlessstr = _('Hide Tags')
            tags = ""
            for tag in self.available_tags:
                if tags:
                    tags += '<span class="gray">|</span>  <a href="" class="addtag_%(name)s" title="%(tag)s">%(tag)s</a> '%{'tag': tag,'name':name}
                else:
                    tags += '<a href="" class="addtag_%(name)s" title="%(tag)s">%(tag)s</a> '%{'tag': tag,'name':name}
            js='''
                <script type="text/javascript">
                     $(document).ready(function() {
                     $("#extrainfo_%(name)s").hide();


                     $("a.addtag_tags").click(function() {
                        val = $("#id_%(name)s").val();
                        newval = $(this).attr('title');
                        if (val.indexOf(' '+newval+ ',') == -1 && val.indexOf(','+newval+ ',') == -1 && val.indexOf(newval+ ',') == -1){
                            if (val == '') val = newval+ ', ';
                            else  val = val + newval+ ', ';
                            $("#id_%(name)s").val(val)
                            $(this).toggleClass('gray')
                        }
                        return false;
                        });



                    $("a#click_extrainfo_%(name)s").toggle(
                      function() {
                        $("#extrainfo_%(name)s").slideDown('fast');
                        $("a#click_extrainfo_%(name)s").text("%(showlessstr)s");
                      },
                      function() {
                        $("#extrainfo_%(name)s").slideUp('fast');
                        $("a#click_extrainfo_%(name)s").text("%(showmorestr)s");
                      }
                    );
                    });
                    </script>'''%{'name':name, 'showlessstr': showlessstr, 'showmorestr': showmorestr }
            div='''
            <a href="" id="click_extrainfo_%(name)s">%(showmorestr)s</a>

                 <div id="extrainfo_%(name)s">
                 <br/>
                %(tags)s
                </div>
              '''%{'name': name, 'tags': tags, 'showmorestr': showmorestr}
            return mark_safe(u'%s %s %s' % (textinput,js, div))
        else:
            return mark_safe(u'%s' % (textinput))


class PermissionsWidget(Widget):
    ch = (('none',_('None')),
          ('view',_('View')),
          ('create', _('View and Create')),
          ('delete', _('View, Create and Edit/Delete')))

    def __init__(self, attrs=None, url=None, autofill=True):
        self.attrs = attrs or {}
        self.url = url
        self.autofill = autofill

    def render(self, name, value, attrs=None):
        output = []
        output.append('<table>')

        for (id,app) in permissions.apps:
            tid = "%s_%s"%(name,id)
            if value:
                tval = value.get(tid)
            else:
                tval = None
            output.append('<tr><td>%s: </td><td>%s</td></tr>'%(app, Select(choices=self.ch).render(tid, tval, {'id': tid})) )
        output.append('</table>')

        return mark_safe(u'\n'.join(output))

    def value_from_datadict(self, data, files, name):
        #access data from initial data dict
        d = data.get(name)
        if d:
            ret = {}
            for (id,app) in permissions.apps:
                tid = "%s_%s"%(name,id)
                ret[tid] = d.get(id, None)
            return ret
        else: #access data from submited form
            ret = {}
            for (id,app) in permissions.apps:
                tid = "%s_%s"%(name,id)
                ret[tid] = data.get(tid, None)
            return ret
        #else no value...
        return None

class PermissionsField(forms.Field):
    widget = PermissionsWidget

    def clean(self, value):
        newval = {}
        for key, value in value.items():
            nkey = key.split('_')[1]
            newval[nkey] = value
        return newval

class MyRadioFieldRenderer(RadioFieldRenderer):
    """
    Special RadioField renderer so we don't get stupid ul-li
    """
    def render(self):
        return mark_safe(u'\n%s\n' % u'\n'.join([u'%s'
                % force_unicode(w) for w in self]))
