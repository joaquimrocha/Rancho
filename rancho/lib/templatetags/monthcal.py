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

from datetime import date, timedelta

from django import template
from milestone.models import Milestone
from django.db.models import Q
import datetime
from granular_permissions.permissions import PERMISSIONS_MESSAGE_VIEW, PERMISSIONS_MILESTONE_VIEW, PERMISSIONS_WIKIBOARD_VIEW, PERMISSIONS_FILE_VIEW, PERMISSIONS_TODO_VIEW
from granular_permissions.permissions import checkperm

register = template.Library()


from datetime import date, timedelta

def get_last_day_of_month(year, month):
    if (month == 12):
        year += 1
        month = 1
    else:
        month += 1
    return date(year, month, 1) - timedelta(1)


def monthcal(user, size = 'small', year = date.today().year, month = date.today().month):
    year, month = int(year), int(month)
    event_list = []
    events = Milestone.objects.filter(Q(responsible = None) | Q(responsible = user), due_date__year = year, due_date__month = month, completion_date = None)
    for event in events:
        project = event.project
        if checkperm(PERMISSIONS_MILESTONE_VIEW, user, project):
            event_list.append(event)
    first_day_of_month = date(year, month, 1)
    last_day_of_month = get_last_day_of_month(year, month)
    first_day_of_calendar = first_day_of_month - timedelta(first_day_of_month.weekday())
    last_day_of_calendar = last_day_of_month + timedelta(7 - last_day_of_month.weekday())

    month_cal = []
    week = []
    week_headers = []

    i = 0
    day = first_day_of_calendar
    while day <= last_day_of_calendar:
        if i < 7:
            week_headers.append(day)
        cal_day = {}
        cal_day['day'] = day
        cal_day['event'] = None
        for event in event_list:
            if day >= event.due_date.date() and day <= day <= event.due_date.date():
                if day < date.today():
                    cal_day['event'] = 'late'
                else:
                    cal_day['event'] = 'upcoming'
        if day.month == month:
            cal_day['in_month'] = True
        else:
            cal_day['in_month'] = False
        if day == date.today():
            cal_day['today'] = True
        week.append(cal_day)
        if day.weekday() == 6:
            month_cal.append(week)
            week = []
        i += 1
        day += timedelta(1)
    #TODO: ROCHA: this has to be refactored to really work for a month
    today = date.today()
    next_month = first_day_of_month + datetime.timedelta(days = 31)
    previous_month = first_day_of_month - datetime.timedelta(days = 5)
    return {'calendar': month_cal, 'headers': week_headers, 'size': size,
            'today': today, 'next_month': next_month, 'previous_month': previous_month, 'current_month': first_day_of_month}

register.inclusion_tag('lib/monthcal.html')(monthcal)
