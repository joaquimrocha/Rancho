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

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response, Http404
from django.template import loader, Context
from django.template.context import RequestContext
from rancho.granular_permissions.permissions import PERMISSIONS_MILESTONE_VIEW, \
    PERMISSIONS_MILESTONE_CREATE, PERMISSIONS_MILESTONE_EDITDELETE, checkperm
from rancho.milestone.models import Milestone



@login_required
def base(request, year = None, month = None):    
    return render_to_response('cal/basecalendar.html', 
                              {'year': year, 'month': month},
                              context_instance=RequestContext(request))
       
@login_required
def get_events(request, year, month, day):
    user = request.user
    import datetime
    from django.db.models import Q
    event_date = datetime.date(int(year), int(month), int(day))
    milestone_list = []
    milestones = Milestone.objects.filter(Q(responsible = None) | Q(responsible = user), due_date__year = year, due_date__month = month, due_date__day = day, completion_date = None)
    for milestone in milestones:
        project = milestone.project
        if checkperm(PERMISSIONS_MILESTONE_VIEW, user, project):
            milestone_list.append(milestone)
    if not milestone_list:
        return Http404()
    result = '''
<taconite>
    {% load i18n usernamegen %}
    <css select="#events_place" name="display" value="none" />
    <replaceContent select="#events_place">
        <p style="margin:20px 0 10px 0;"><span class="smallcaps_title gray_bg">{{ event_date|date:"l, d N Y" }}</span></p>
        {% for milestone in milestone_list %}
        <div style="overflow: hidden; margin: 0 0 5px 15px; border-bottom: 1px solid #afafaf; padding-bottom: 2px;">
            <div style="float: left; width: 100px; background: #EBF0FA;">
                <p><img src="/media/basepage/images/icons/clock.png" class="textcenter"/> <strong>{% trans "Milestone" %}</strong></p>
            </div>
            <div style="float: left; width: 450px;">
                <div style="float: left;">
                    <p style="margin-left: 15px;"><a href="{% url milestone.views.list p_id=milestone.project.id %}"><span {% if milestone.completion_date %}class="linethrough"{% endif %}>{{ milestone.title }}</span></a></p>
                </div>
                <div style="float: right;">
                    <p><span class="gray">{% trans "Assigned to" %}</span> {% if milestone.responsible %}{% usernamegen milestone.responsible %}{% else %}Anyone{% endif %}</p>
                </div>
            </div>
        </div>
        {% endfor %}
    </replaceContent>
    <slideDown select="#events_place" value="1800" /> 
</taconite>
'''
    result = loader.get_template_from_string(result).render(Context({'user': user, 'milestone_list': milestone_list, 'event_date': event_date}))
    return HttpResponse(result, mimetype='text/xml')
