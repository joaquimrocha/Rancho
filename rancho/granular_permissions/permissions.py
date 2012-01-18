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

from django.utils.translation import ugettext as _

apps = [('message',_('Messages')), ('todo',_('ToDos')), ('milestone',_('Milestones')), ('wikiboard',_('Wikiboards')), ('file',_('Files')) ]

PERMISSIONS_MESSAGE_VIEW   = 'message_view'
PERMISSIONS_MESSAGE_CREATE = 'message_create'
PERMISSIONS_MESSAGE_EDITDELETE = 'message_delete'
PERMISSIONS_TODO_VIEW   = 'todo_view'
PERMISSIONS_TODO_CREATE = 'todo_create'
PERMISSIONS_TODO_EDITDELETE = 'todo_delete'
PERMISSIONS_MILESTONE_VIEW   = 'milestone_view'
PERMISSIONS_MILESTONE_CREATE = 'milestone_create'
PERMISSIONS_MILESTONE_EDITDELETE = 'milesonte_delete'
PERMISSIONS_WIKIBOARD_VIEW   = 'wikiboard_view'
PERMISSIONS_WIKIBOARD_CREATE = 'wikiboard_create'
PERMISSIONS_WIKIBOARD_EDITDELETE = 'wikiboard_delete'
PERMISSIONS_FILE_VIEW   = 'file_view'
PERMISSIONS_FILE_CREATE = 'file_create'
PERMISSIONS_FILE_EDITDELETE = 'file_delete'

IS_ADMIN = 'admin'
IS_ACCOUNT_OWNER = 'account_owner'

def check_user_permission(perm, user, object):
    """
    user can allways edit/delete own objects
    """
    if perm == PERMISSIONS_MESSAGE_EDITDELETE or \
       perm == PERMISSIONS_TODO_EDITDELETE or \
       perm ==  PERMISSIONS_MILESTONE_EDITDELETE or \
       perm == PERMISSIONS_WIKIBOARD_EDITDELETE or \
       perm == PERMISSIONS_FILE_EDITDELETE:
        return object.creator == user
    else:
        return False

def check_project_permission(perm, project):
    """
    if project is finished user's can only view data,
    not change it (including admins)
    """
    if project.status == 'F':
        if perm == PERMISSIONS_MESSAGE_VIEW or \
            perm == PERMISSIONS_TODO_VIEW or \
            perm ==  PERMISSIONS_MILESTONE_VIEW or \
            perm == PERMISSIONS_WIKIBOARD_VIEW or \
            perm == PERMISSIONS_FILE_VIEW:
                return True
        else:
            return False
    else:
        return True


def checkperm(perm, user, project, object=None):
    """
    checks if a user has a given permission on project
    or if is creator of object
    """
    if perm==None:
        return True
    if perm==IS_ADMIN:
        return user.is_superuser
    if perm==IS_ACCOUNT_OWNER:
        return user.get_profile.is_account_owner

    if object:
        res1 = check_user_permission(perm, user, object)
    else:
        res1 = False
    if project:
        res2 = user.has_row_perm(project, perm)
    else:
        res2 = False

    if not check_project_permission(perm, project):
        return False
    else:
        return res1 or res2

def get_permission_dictionary(user, project):

    perm = {}
    if user.has_row_perm(project, PERMISSIONS_MESSAGE_EDITDELETE):
        perm['message'] = 'delete'
    elif user.has_row_perm(project, PERMISSIONS_MESSAGE_CREATE):
        perm['message'] = 'create'
    elif user.has_row_perm(project, PERMISSIONS_MESSAGE_VIEW):
        perm['message'] = 'view'
    else:
        perm['message'] = 'none'

    if user.has_row_perm(project, PERMISSIONS_TODO_EDITDELETE):
        perm['todo'] = 'delete'
    elif user.has_row_perm(project, PERMISSIONS_TODO_CREATE):
        perm['todo'] = 'create'
    elif user.has_row_perm(project, PERMISSIONS_TODO_VIEW):
        perm['todo'] = 'view'
    else:
        perm['todo'] = 'none'

    if user.has_row_perm(project, PERMISSIONS_MILESTONE_EDITDELETE):
        perm['milestone'] = 'delete'
    elif user.has_row_perm(project, PERMISSIONS_MILESTONE_CREATE):
        perm['milestone'] = 'create'
    elif user.has_row_perm(project, PERMISSIONS_MILESTONE_VIEW):
        perm['milestone'] = 'view'
    else:
        perm['milestone'] = 'none'

    if user.has_row_perm(project, PERMISSIONS_WIKIBOARD_EDITDELETE):
        perm['wikiboard'] = 'delete'
    elif user.has_row_perm(project, PERMISSIONS_WIKIBOARD_CREATE):
        perm['wikiboard'] = 'create'
    elif user.has_row_perm(project, PERMISSIONS_WIKIBOARD_VIEW):
        perm['wikiboard'] = 'view'
    else:
        perm['wikiboard'] = 'none'

    if user.has_row_perm(project, PERMISSIONS_FILE_EDITDELETE):
        perm['file'] = 'delete'
    elif user.has_row_perm(project, PERMISSIONS_FILE_CREATE):
        perm['file'] = 'create'
    elif user.has_row_perm(project, PERMISSIONS_FILE_VIEW):
        perm['file'] = 'view'
    else:
        perm['file'] = 'none'

    return perm
