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

from PIL import Image
from cStringIO import StringIO
from django.contrib.auth.models import User
from django.core import urlresolvers
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from rancho import granular_permissions, settings
from rancho.file.models import FileVersion, File
from rancho.granular_permissions.permissions import PERMISSIONS_MESSAGE_VIEW, \
    PERMISSIONS_MILESTONE_VIEW, PERMISSIONS_WIKIBOARD_VIEW, PERMISSIONS_FILE_VIEW, \
    PERMISSIONS_TODO_VIEW, checkperm
from rancho.lib.templatetags.usernamegen import usernamegen
from rancho.message.models import Message
from rancho.milestone.models import Milestone
from rancho.tagging.models import Tag
from rancho.todo.models import ToDo, ToDo_in_ToDoList
from rancho.wikiboard.models import WikiEntry
from random import Random
import mimetypes
import os
import sys
import string

def save_image(dbclass, name, image, image_size, dbclass_image_attribute = 'picture', format = 'JPEG'):
    
    image_object = Image.open(StringIO(image.read()))
    file_name = '%s.%s' % (name, format.lower())
    try:
        os.makedirs(os.path.dirname(file_name))
    except:
        pass
    picturefile = StringIO()
    image_object.thumbnail(image_size, Image.ANTIALIAS)
    image_object.save(picturefile, format.upper())
    image_content = ContentFile(picturefile.getvalue())
    eval('dbclass.' + dbclass_image_attribute + '.save(file_name, image_content, save = True)')    
    picturefile.close()

def format_users_for_dropdown(me, users_list):
    formated_users = [(0, _('Anyone'))]
    for user in users_list:
        if user != me:
            formated_name = usernamegen(user)
        else:
            formated_name = _('Myself: %s')%usernamegen(user)
        
        formated_users.append((user.id, formated_name))
    return formated_users


def get_site_tags():
    """
    gets the tags used on the site
    """
    a = set([str(name) for name in Tag.objects.usage_for_model(File)])
    b = set([str(name) for name in Tag.objects.usage_for_model(Message)])
    return a.union(b) 

def get_object_overview_info(object):
    '''
    Returns a small icon and friendly name for the given object.
    '''
    icons_folder = '/media/basepage/images/icons/'
    complete = False
    if isinstance(object, Message):
        url = urlresolvers.reverse('rancho.message.views.read_add_comment', args = [object.project.id, object.id])
        action = _('Posted by')
        return (_('Message'), icons_folder + 'comment.png', object.title, object.creator, action, complete, url)
    elif isinstance(object, Milestone):
        action = _('Assigned to')
        url = urlresolvers.reverse('rancho.milestone.views.list', args = [object.project.id])
        if object.completion_date:
            action = _('Completed by')
            complete = True
        return (_('Milestone'), icons_folder + 'clock.png', object.title, object.responsible, action, complete, url)
    elif isinstance(object, ToDo):
        action = _('Assigned to')
        todolist = ToDo_in_ToDoList.objects.filter(todo = object)[0].todolist
        url = urlresolvers.reverse('rancho.todo.views.view_todo_list', kwargs = {'p_id': todolist.project.id, 'todo_list_id': todolist.id})
        if object.completion_date:
            action = _('Completed by')
            complete = True
        return (_('ToDo'), icons_folder + 'note.png', object.description, object.responsible, action, complete, url)
    elif isinstance(object, WikiEntry):
        action = _('By')
        url = urlresolvers.reverse('rancho.wikiboard.views.view_page', args = [object.wiki.project.id, object.wiki.id, object.id])
        return (_('Wikiboard'), icons_folder + 'page.png', object.wiki.name, object.wiki.creator, action, complete, url)
    elif isinstance(object, FileVersion):
        action = _('Uploaded by')
        url = urlresolvers.reverse('rancho.file.views.view_file', kwargs = {'p_id': object.file.project.id, 'file_id': object.file.id})
        return (_('File'), icons_folder + 'page_white_put.png', object.file.title, object.creator, action, complete, url)
    return '', '', '', '', '', '', ''

def get_overview(user, project):
    """
    only get object user can view
    """    
    if checkperm(PERMISSIONS_WIKIBOARD_VIEW, user, project ):
        wikiboards = WikiEntry.objects.filter(wiki__project = project, wiki__project__status='A').order_by('-creation_date')
        wikiboards_ids = [(wiki_object.creation_date, 'wikiboards_%s' % wiki_object.id) for wiki_object in wikiboards[:50]]
    else:
        wikiboards_ids = []
    
    if checkperm(PERMISSIONS_MESSAGE_VIEW, user, project ):
        messages = Message.objects.filter(project = project, project__status='A').extra(where=['message_message.initial_message_id = message_message.id']).order_by('-creation_date')
        messages_ids = [(message_object.creation_date, 'messages_%s' % message_object.id) for message_object in messages[:50]]
    else:
        messages_ids = []
    
    if checkperm(PERMISSIONS_MILESTONE_VIEW, user, project ):
        milestones = Milestone.objects.filter(project = project, project__status='A', completion_date__isnull = True).order_by('-creation_date')
        milestones_ids = [(milestone_object.creation_date, 'milestones_%s' % milestone_object.id) for milestone_object in milestones[:50]]
        
        completemilestones = Milestone.objects.filter(project = project, project__status='A', completion_date__isnull = False).order_by('-completion_date')
        completemilestones_ids = [(milestone_object.completion_date, 'completemilestones_%s' % milestone_object.id) for milestone_object in completemilestones[:50]]
    else:
        milestones_ids = completemilestones_ids = []
    
    if checkperm(PERMISSIONS_FILE_VIEW, user, project ):
        files = FileVersion.objects.filter(file__project = project, file__project__status='A').order_by('-creation_date')
        files_ids = [(file_object.creation_date, 'files_%s' % file_object.id) for file_object in files[:50]]
    else:
        files_ids = []
    
    if checkperm(PERMISSIONS_TODO_VIEW, user, project ):
        todos_in_todolists = ToDo_in_ToDoList.objects.filter(todolist__project = project, todolist__project__status='A', todo__completion_date__isnull = True).order_by('-todo__creation_date')
        todos_ids_list = [todo_in_todolist.todo.id for todo_in_todolist in todos_in_todolists]
        todos = ToDo.objects.filter(id__in=todos_ids_list)
        todos_ids = [(todo_object.creation_date, 'todos_%s' % todo_object.id) for todo_object in todos[:50]]
        
        completetodos_in_todolists = ToDo_in_ToDoList.objects.filter(todolist__project = project, todolist__project__status='A', todo__completion_date__isnull = False).order_by('-todo__completion_date')
        completetodos_ids_list = [todo_in_todolist.todo.id for todo_in_todolist in completetodos_in_todolists]
        completetodos = ToDo.objects.filter(id__in=completetodos_ids_list)
        completetodos_ids = [(todo_object.completion_date, 'completetodos_%s' % todo_object.id) for todo_object in completetodos[:50]]
    else:
        todos_ids = completetodos_ids = []        
    
    all_events = messages_ids + milestones_ids + completemilestones_ids + wikiboards_ids + files_ids + todos_ids + completetodos_ids
    all_events.sort()
    all_events.reverse()
    sorted_events = []
    for event in all_events:
        object = eval('%s.get(id = %s)' % tuple(event[1].split('_')))
        try:
            if object.completion_date:
                setattr(object, 'overview_date', object.completion_date.date)
            else:
                setattr(object, 'overview_date', object.creation_date.date)
        except AttributeError:
            setattr(object, 'overview_date', object.creation_date.date)
        sorted_events.append(object)
    return sorted_events


def send_file(filename, size=0):    
    class FileIterWrapper(object):
        def __init__(self, flo, chunk_size = 1024**2):
            self.flo = flo
            self.chunk_size = chunk_size
    
        def next(self):
            data = self.flo.read(self.chunk_size)
            if data:
                return data
            else:
                raise StopIteration
    
        def __iter__(self):
            return self

    content_type, encoding = mimetypes.guess_type(filename) 
    if not content_type: content_type = 'application/octet-stream'
    #should add here more ways to serve files... (ngix, lighttpd., etc)
    if settings.HOW_SEND_FILE == 'apache-modsendfile':    
        print >> sys.stderr, os.path.basename(filename), content_type, size
        response = HttpResponse() 
        response['X-Sendfile'] =  filename
        response['Content-Type'] = content_type 
        response['Content-Length'] = size
        #response['Content-Disposition'] = 'attachment; filename="%s"' % filename 
        response['Content-Disposition'] = 'inline; filename="%s"' % os.path.basename(filename)
        return response
    else:
        return HttpResponse(FileIterWrapper(open( filename )), content_type=content_type)

def gen_random_pass():
    return ''.join( Random().sample(string.letters+string.digits, 12) )            

def get_users_to_notify(project, perm):
    users_with_perm = granular_permissions.get_users_with_permission(project, perm)
    superuser = User.objects.filter(is_superuser=True)
    return (users_with_perm | superuser ).distinct().order_by('userprofile__company')