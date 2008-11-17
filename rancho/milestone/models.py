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

from django.db import models
from django.contrib.auth.models import User

from rancho.project.models import Project

from datetime import date


class MilestoneManager(models.Manager):    
    def get_late_milestones(self, project = None, order = '-due_date', user = None):
        milestones = Milestone.objects.filter(completion_date = None).order_by(order)
        if project:
            milestones = milestones.filter(project = project).order_by(order)
        if user:
            milestones = milestones.filter(models.Q(responsible = user) | models.Q(responsible = None)).order_by(order)
        return [milestone for milestone in milestones if milestone.due_date.date() <= date.today()]
    
    def get_upcoming_milestones(self, project = None, order = 'due_date', user = None):
        milestones = Milestone.objects.filter(completion_date = None).order_by(order)
        if project:
            milestones = milestones.filter(project = project).order_by(order)
        if user:
            milestones = milestones.filter(models.Q(responsible = user) | models.Q(responsible = None)).order_by(order)
        return [milestone for milestone in milestones if milestone.due_date.date() > date.today()]
    
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
    #Se null e o projecto todo o responsavel
    responsible = models.ForeignKey(User, related_name='responsible', null=True)
    title = models.CharField(max_length=50)
    creation_date = models.DateTimeField(auto_now_add = True)
    due_date = models.DateTimeField()
    send_notification_email = models.BooleanField()
    completion_date = models.DateTimeField(null=True)
    sent_notification = models.BooleanField(default=False)
    objects = MilestoneManager()
    
