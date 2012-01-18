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

from datetime import date, datetime
from django.contrib.auth.models import User
from django.db import models
from rancho.project.models import Project

class MilestoneManager(models.Manager):
    def get_late_milestones(self, project = None, order = '-due_date', user = None):
        milestones = Milestone.objects.filter(completion_date = None).order_by(order)
        if project:
            milestones = milestones.filter(project = project).order_by(order)
        if user:
            milestones = milestones.filter(models.Q(responsible = user) | models.Q(responsible = None)).order_by(order)
        return [milestone for milestone in milestones if milestone.is_late()]

    def get_upcoming_milestones(self, project = None, order = 'due_date', user = None):
        milestones = Milestone.objects.filter(completion_date = None).order_by(order)
        if project:
            milestones = milestones.filter(project = project).order_by(order)
        if user:
            milestones = milestones.filter(models.Q(responsible = user) | models.Q(responsible = None)).order_by(order)
        return [milestone for milestone in milestones if milestone.is_upcoming()]

    def get_complete_milestones(self, project = None, order = 'completion_date', user = None):
        milestones = Milestone.objects.all().exclude(completion_date = None).order_by(order)
        if project:
            milestones = milestones.filter(project = project).order_by(order)
        if user:
            milestones = milestones.filter(models.Q(responsible = user) | models.Q(responsible = None)).order_by(order)
        return milestones

class Milestone(models.Model):
    creator = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    #If null, all the project is responsible
    responsible = models.ForeignKey(User, related_name='responsible', null=True)
    title = models.CharField(max_length=500)
    creation_date = models.DateTimeField(default = datetime.now())
    due_date = models.DateTimeField()
    send_notification_email = models.BooleanField()
    completion_date = models.DateTimeField(null=True)
    sent_notification = models.BooleanField(default=False)

    objects = MilestoneManager()

    @models.permalink
    def get_absolute_url(self):
        return ('rancho.milestone.views.edit', [], {'p_id': self.project.id, 'milestone_id':self.id})

    def is_late(self):
        return self.due_date.date() <= date.today() and \
               not self.completion_date

    def is_upcoming(self):
        return self.due_date.date() > date.today() and \
               not self.completion_date

    def is_complete(self):
        return self.completion_date != None

    def get_status_name(self):
        if self.is_late():
            return 'late'
        elif self.is_upcoming():
            return 'upcoming'
        else:
            return 'complete'

    def _get_todolist(self):
        todolist_set = self.todo_milestone.all()
        if todolist_set:
            return todolist_set[0]
        return None

    todolist = property(_get_todolist)
