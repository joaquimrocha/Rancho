#-*- coding: utf-8 -*-
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

from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponseRedirect
from rancho import settings
from rancho.company.models import Company, Company
from rancho.file.models import File, FileVersion
from rancho.granular_permissions.permissions import PERMISSIONS_TODO_EDITDELETE, \
    PERMISSIONS_TODO_CREATE, PERMISSIONS_TODO_VIEW, PERMISSIONS_MILESTONE_EDITDELETE, \
    PERMISSIONS_MILESTONE_CREATE, PERMISSIONS_MILESTONE_VIEW, \
    PERMISSIONS_WIKIBOARD_EDITDELETE, PERMISSIONS_WIKIBOARD_CREATE, \
    PERMISSIONS_WIKIBOARD_VIEW, PERMISSIONS_FILE_EDITDELETE, PERMISSIONS_FILE_CREATE, \
    PERMISSIONS_FILE_VIEW, PERMISSIONS_MESSAGE_EDITDELETE, \
    PERMISSIONS_MESSAGE_CREATE, PERMISSIONS_MESSAGE_VIEW, get_permission_dictionary
from rancho.lib.utils import create_archive, extract_archive, send_file
from rancho.message.models import Message
from rancho.milestone.models import Milestone
from rancho.project.models import Project, UserInProject
from rancho.todo.models import ToDoList, ToDo
from rancho.user.models import UserProfile
from rancho.wikiboard.models import Wiki, WikiEntry
from settings import MEDIA_ROOT, UPLOAD_DIR, PEOPLE_DIR, PROJECT_DIR, \
    EXPORTATION_PREFIX, IMPORTATION_PREFIX
import os
import shutil
import tempfile
import zipfile
try: #support python<=2.4
    from xml.etree import ElementTree as ET
except: #python 2.5
    from elementtree import ElementTree as ET

# Important element names to make it easier 
# in case they need to be changed 
ROOT_ELEMENT = 'account'
USERS_ELEMENT = 'users'
PERMISSIONS_ELEMENT = 'permissions'

def export_account(name_prefix, components = []):
    files = []
    root = ET.Element(ROOT_ELEMENT)
    # Users
    users = ET.SubElement(root, USERS_ELEMENT)
    for user in User.objects.all():
        user_element = serialize(user)
        user_profile = user.get_profile()
        if user_profile.small_photo:
            file = os.path.basename(user_profile.small_photo.path)
            files.append(os.path.join(PEOPLE_DIR, file))
        if user_profile.large_photo:
            file = os.path.basename(user_profile.large_photo.path)
            files.append(os.path.join(PEOPLE_DIR, file))
        user_element.append(serialize(user_profile))
        users.append(user_element)
    # Companies
    companies = ET.SubElement(root, 'companies', {'type': 'list'})
    for company in Company.objects.all():
        companies.append(serialize(company))
    # Projects
    projects = ET.SubElement(root, 'projects', {'type': 'list'})
    for project in Project.objects.all():
        project_element = serialize(project)
        if project.logo:
            file = os.path.basename(project.logo.path)
            files.append(os.path.join(PROJECT_DIR, file))
        projects.append(project_element)
        serializeUsersInProject(project_element, project)
        #Messages
        if 'M' in components:
            serializeMessages(project_element, project)
        #ToDos
        if 'T' in components:
            serializeToDos(project_element, project)
        # Milestones
        if 'S' in components:
            serializeMilestones(project_element, project)
        # Wikiboards
        if 'W' in components:
            serializeWikiboards(project_element, project)
        # Files
        if 'F' in components:
            files += serializeFiles(project_element, project)
    indent(root)
    now = datetime.now()
    export_temp_dir = tempfile.mkdtemp(prefix = EXPORTATION_PREFIX) 
    export_name = '%s-%s%s%s%s%s%s%s' % (name_prefix, now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond)
    export_path = os.path.join(export_temp_dir, export_name)
    os.mkdir(export_path)
    tree = ET.ElementTree(root)
    tree.write(os.path.join(export_path, 'export.xml'), encoding = 'UTF-8')
    for file in files:
        new_dir = os.path.join(export_path, os.path.dirname(file))
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        shutil.copy(os.path.join(MEDIA_ROOT, file), os.path.join(export_path, file))
    zip_name = os.path.join(export_temp_dir, '%s.zip' % export_name)
    create_archive(export_path, zip_name)
    return send_file(zip_name)

def serialize(object, name = None, quiet = True, exclude = []):
    element_name = name or object._meta.object_name
    element = ET.Element(element_name)
    for field in object._meta.fields:
        if field.name in exclude:
            continue
        value = getattr(object, field.name)
        if value or value == 0 or not quiet:
            if isinstance(value, models.base.Model):
                value = getattr(value, value._meta.pk.name)
            field_element = ET.SubElement(element, field.name)
            type_name = type(value).__name__
            if type_name == 'ImageFieldFile':
                type_name = 'text'
            elif type_name == 'FieldFile':
                type_name = 'text'
            elif type_name == 'unicode':
                type_name = 'text'
            field_element.set('type', type_name)
            field_element.text = unicode(value)
    return element

def serializeMessages(element, project):
    messages_in_project = Message.objects.get_messages(project = project)
    if not messages_in_project:
        return
    messages_element = ET.SubElement(element, 'messages', {'type': 'list'})
    for message in messages_in_project:
        message_element = serialize(message)
        messages_element.append(message_element)
        comments = message.get_comments()
        if comments:
            comments_element = ET.SubElement(message_element, 'comments', {'type': 'list'})
        for comment in comments:
            comments_element.append(serialize(comment))

def serializeUsersInProject(element, project):
    users_in_project = UserInProject.objects.filter(project = project)
    if not users_in_project:
        return
    users_in_project_element = ET.SubElement(element, 'users', {'type': 'list'})
    for user_in_project in users_in_project:
        user_in_project_element = serialize(user_in_project)
        users_in_project_element.append(user_in_project_element)
        permission_dict = get_permission_dictionary(user_in_project.user, project)
        permissions_element = ET.SubElement(user_in_project_element, 'permissions', {'type': 'list'})
        for key in permission_dict.keys():
            permission_element = ET.SubElement(permissions_element, key, {'type': 'text'})
            permission_element.text = permission_dict[key] 

def serializeMilestones(element, project):
    milestones = Milestone.objects.filter(project = project)
    if not milestones:
        return
    milestones_element = ET.SubElement(element, 'milestones', {'type': 'list'})
    for milestone in milestones:
        milestones_element.append(serialize(milestone))

def serializeWikiboards(element, project):
    wikiboards = Wiki.objects.filter(project = project)
    if  not wikiboards:
        return
    wikiboards_element = ET.SubElement(element, 'wikiboards', {'type': 'list'})
    for wikiboard in wikiboards:
        wikiboard_element = serialize(wikiboard)
        wikiboards_element.append(wikiboard_element)
        entries = WikiEntry.objects.filter(wiki = wikiboard)
        if not entries:
            continue
        entries_element = ET.SubElement(wikiboard_element, 'entries', {'type': 'list'})
        for entry in entries:
            entries_element.append(serialize(entry))

def serializeToDos(element, project): 
    todo_lists = ToDoList.objects.filter(project = project)
    if not todo_lists:
        return
    todo_lists_element = ET.SubElement(element, 'todo_lists', {'type': 'list'})
    for todo_list in todo_lists:
        todo_list_element = serialize(todo_list)
        todo_lists_element.append(todo_list_element)
        todo_items = ToDo.objects.filter(todo_list = todo_list)
        if not todo_items:
            continue
        todo_items_element = ET.SubElement(todo_list_element, 'todo_items', {'type': 'list'})
        for item in todo_items:
            todo_items_element.append(serialize(item))

def serializeFiles(element, project):
    files_list = []
    files = File.objects.filter(project = project)
    if not files:
        return []
    files_element = ET.SubElement(element, 'files', {'type': 'list'})
    for file in files:
        file_element = serialize(file)
        files_element.append(file_element)
        versions = FileVersion.objects.filter(file = file)
        if not versions:
            continue
        versions_element = ET.SubElement(file_element, 'versions', {'type': 'list'})
        for version in versions:
            file_name = os.path.basename(version.file_location.path)
            files_list.append(os.path.join(UPLOAD_DIR, file_name))
            versions_element.append(serialize(version))
    return files_list

def indent(element, level = 0):
    i = "\n%s" % ("    " * level)
    if len(element):
        if not element.text or not element.text.strip():
            element.text = i + "    "
        if not element.tail or not element.tail.strip():
            element.tail = i
        for element in element:
            indent(element, level + 1)
        if not element.tail or not element.tail.strip():
            element.tail = i
    elif level and (not element.tail or not element.tail.strip()):
            element.tail = i


def import_account(import_file, system = None):
    EXPORT_XML_FILE_NAME = 'export.xml'
    # Dictionary with matches between the XML's objects' IDs
    # and the IDs newly created
    references = {}
    synonims = {'User': ['user', 'author', 'responsible', 'creator'], 
                'Company': ['company'], 'Project': ['project'], 
                'Wiki': ['wiki'], 'File': ['file'],
                'ToDoList': ['todolist', 'todo_list'], 'ToDo': ['todo'], 
                'Message': ['initial_message', 'message']}
    existence_checks = {'User': ['username'], 'Company': ['short_name'], 
                        'UserProfile': ['user'], 'Project': ['name'], 
                        'Wiki': ['name'], 'UserInProject': ['user', 'project']}
    self_references = ['Message.initial_message']
    
    if type(import_file) == str:
         import_file_path = import_file
    else:
        export_temp_dir = tempfile.mkdtemp(prefix = IMPORTATION_PREFIX)
        import_file_path = os.path.join(export_temp_dir, 'importation_file.zip')
        import_file_object = open(import_file_path, 'wb+')
        for chunk in import_file.chunks():
            import_file_object.write(chunk)
        import_file_object.close()
    exportation_base_dir = extract_archive(import_file_path)
    files_in_dir = os.listdir(exportation_base_dir)
    if len(files_in_dir) > 1 or not files_in_dir:
        return
    
    # Check importation system
    if system == 'BASECAMP':
        exportation_file = os.path.join(exportation_base_dir, files_in_dir[0])
    else:
        exportation_base_dir = os.path.join(exportation_base_dir, files_in_dir[0])
        files_in_dir = os.listdir(exportation_base_dir)
        if not EXPORT_XML_FILE_NAME in files_in_dir:
            return
        exportation_file = os.path.join(exportation_base_dir, EXPORT_XML_FILE_NAME)
    tree = ET.parse(exportation_file)
    
    if system == 'BASECAMP':
        tree = convert_bc2rancho(tree)
    
    def get_children(element, sub_element):
        sub_element_node = element.find(sub_element)
        if sub_element_node:
            return sub_element_node.getchildren()
        return []
    
    def add_to_references(element, id):
        if not element.tag in references.keys():
            references[element.tag] = {}
        references[element.tag][element.find('id').text] = id
    
    def get_object_by_reference(name, reference):
        real_name = ''
        if name in references.keys():
            real_name = name
        else:
            for key, names in synonims.items():
                if name in names:
                    real_name = key
                    break
        if real_name:
            return eval('%s.objects.get(id = %s)' % (real_name, references[real_name].get(reference)))
        return
    
    def elementToVar(element):
        type_name = element.attrib.get('type')
        var = element.text
        if type_name:
            if type_name == 'datetime':
                var = 'datetime.strptime("%s".split(".")[0], "%%Y-%%m-%%d %%H:%%M:%%S")' % var
            elif type_name == 'text':
                if var:
                    var = 'u"""%s"""' % var.replace('"', '\\"')
                else:
                    var = ''
            elif type_name == 'bool':
                if var:
                    var = var.lower() == 'true'
                else:
                    var = False
            else:
                var = '%s("%s")' % (type_name, var)
        return '%s = %s' % (element.tag, var)

    def unserialize(element, ignore_children = []):
        args = []
        list_elements = []
        post_args = {}
        id = ''
        new_object = None
        if element.tag in existence_checks.keys():
            fields_list = []
            for element_to_check in existence_checks[element.tag]:
                field = element.find(element_to_check)
                field_name = field.tag
                field_value = '"%s"' % field.text
                if field.attrib.get('type').strip() == 'int':
                    field_name += '__id'
                    field_value = None
                    reference_object = get_object_by_reference(field.tag, field.text)
                    if reference_object:
                        field_value = reference_object.id
                fields_list.append('%s = %s' % (field_name, field_value))
            query = eval('%s.objects.filter(%s)' % (element.tag, ', '.join(fields_list)))
            if query:
                new_object = query[0]
        if not new_object:
            self_references_to_assign = []
            for child in element.getchildren():
                if child.tag in ignore_children:
                    continue
                elif ('%s.%s' % (element.tag, child.tag)) in self_references:
                    self_references_to_assign.append((element.tag, child.tag, child.text))
                    continue
                if child.attrib.get('type') == 'list':
                    list_elements.append(child)
                elif child.tag == 'id':
                    id = element, child.text
                else:                    
                    object = get_object_by_reference(child.tag, child.text)
                    if object:
                        post_args[child.tag] = object
                    else:
                        args.append(elementToVar(child))
            code = '%s(%s)' % (element.tag, ', '.join(args))
            new_object = eval(code)
            
            for key, object in post_args.items():
                setattr(new_object, key, object)
            
            new_object.save()
            add_to_references(element, new_object.id)
            for (object_name, reference, value) in self_references_to_assign:
                a = get_object_by_reference(object_name, value)
                setattr(new_object, reference, get_object_by_reference(object_name, value))
                new_object.save()
        add_to_references(element, new_object.id)
        return new_object
    
    def unserialize_recursive(element, ignore = []):
        unserialize(element)
        for sub_element in element.getchildren():
            if sub_element.attrib.get('type') == 'list':
                for child in sub_element.getchildren():
                    unserialize_recursive(child)
    
    def unserialize_circular_references(element_list, sub_element_list, field):
        for element in element_list.getchildren():
            reference = element.find(field)
            new_object = unserialize(element, [field])
            class_for_field = ''
            last_child = None
            for field_element in get_children(element, sub_element_list):
                if not class_for_field:
                    class_for_field = field_element.tag 
                last_child = unserialize(field_element)
            if class_for_field:
                if reference:
                    setattr(new_object, field, get_object_by_reference(class_for_field, reference.text))
                else:
                    setattr(new_object, field, last_child)
            new_object.save()
    
    # Companies
    for company in tree.find('companies').getchildren():
        unserialize(company)
    
    # Users
    for user in tree.find('users').getchildren():
        unserialize(user, ['UserProfile'])
        user_profile = user.find('UserProfile')
        unserialize(user_profile)
    
    # Projects
    for project in tree.find('projects').getchildren():
        project_object = unserialize(project)
        # User in Project
        for user_element in project.find('users').getchildren():
            user = unserialize(user_element).user
            for permission in user_element.find('permissions').getchildren():
                permission_type = permission.text
                permission_component = permission.tag
                if permission_type == 'delete':
                    permission_type = 'EDITDELETE'
                elif permission_type == 'none':
                    permission_type = 'VIEW'
                else:
                    permission_type = permission_type.upper()
                permission_value = eval('PERMISSIONS_%s_%s' % (permission_component.upper(), permission_type))
                user.add_row_perm(project_object, permission_value)
                user.save()
        for element_list in project.getchildren():
            if element_list.tag == 'files':
                unserialize_circular_references(element_list, 'versions', 'last_file_version')
            elif element_list.tag == 'wikiboards':
                unserialize_circular_references(element_list, 'entries', 'last_version')
            elif element_list.attrib.get('type') == 'list' and \
            element_list.tag != 'users':
                for child in element_list.getchildren():
                    unserialize_recursive(child)
    return


def convert_bc2rancho(tree): 
    
    def convert_date(str):        
        from datetime import datetime
        return datetime.strptime(str, "%Y-%m-%d")
        
    def convert_datetime(str):        
        from datetime import datetime
        return datetime.strptime(str.split(".")[0], "%Y-%m-%dT%H:%M:%SZ")
    
    def process_user(person, company_id, timezone):
        def get_im_service(serv):
            if serv == 'MSN':
                return 'M'
            elif serv == 'AOL':
                return 'A'
            else:
                return 'J'
            
        administrator = person.find('administrator')         
        if hasattr(administrator, 'text') :            
            is_superuser = administrator.text == 'true' 
        else:
            is_superuser = False
            
        deleted = person.find('deleted').text == 'true'
        id = person.find('id').text
        
        user = ET.Element('User')
        add_subelement(user, 'id', 'int', id)
        add_subelement(user, 'username', 'text', person.find('user-name').text)
        add_subelement(user, 'first_name', 'text', person.find('first-name').text)
        add_subelement(user, 'last_name', 'text', person.find('last-name').text)
        add_subelement(user, 'email', 'text', person.find('email-address').text)
        add_subelement(user, 'is_superuser', 'bool', is_superuser)
        add_subelement(user, 'is_active', 'bool', not deleted)
        add_subelement(user, 'id', 'text', id)
        
        user_profile = ET.Element('UserProfile')
        add_subelement(user_profile, 'id', 'int', id)
        add_subelement(user_profile, 'user', 'int', id)
        add_subelement(user_profile, 'company', 'int', company_id)
        add_subelement(user_profile, 'language', 'text', settings.LANGUAGE_CODE)
        add_subelement(user_profile, 'timezone', 'text', timezone)
        add_subelement(user_profile, 'office_phone', 'text', person.find('phone-number-office').text)
        add_subelement(user_profile, 'office_phone_ext', 'text', person.find('phone-number-office-ext').text)
        add_subelement(user_profile, 'mobile_phone', 'text', person.find('phone-number-mobile').text)
        add_subelement(user_profile, 'home_phone', 'text', person.find('phone-number-home').text)
        add_subelement(user_profile, 'im_name', 'text', person.find('im-handle').text)
        add_subelement(user_profile, 'im_service', 'text', get_im_service(person.find('im-service').text))
        
        user.append(user_profile)
                                
        return id,user
    
    def add_subelement(element, name, type_name, value):
        if value: #add only if not null            
            field_element = ET.SubElement(element, name)
            field_element.set('type', type_name)
            if type_name == 'text':
                field_element.text = unicode(value).replace('\n', '\\n').replace('"', '\"').replace("'", "\\'")
            else:
                field_element.text = unicode(value)
    
    def process_company(firm, main):  
        def get_timezone(tz):
            import pytz
            for t in pytz.all_timezones:
                if t.find(tz) > -1:
                    return t
            return None

        id =  firm.find('id').text
        ad1 = firm.find('address-one').text
        ad2 = firm.find('address-two').text
        mailing_address = ''
        if ad1: mailing_address = ad1
        if ad2: mailing_address += ad2
        timezone =  get_timezone(firm.find('time-zone-id').text)
        
        element = ET.Element('Company')
        add_subelement(element, 'id', 'int', id)
        add_subelement(element, 'short_name', 'text', firm.find('name').text)
        add_subelement(element, 'long_name', 'text', firm.find('name').text)        
        add_subelement(element, 'display_logo_name', 'bool', 'False')
        add_subelement(element, 'main_company', 'bool', main)
        add_subelement(element, 'mailing_address', 'text', mailing_address)
        add_subelement(element, 'webpage', 'text', firm.find('web-address').text)
                
        return id, element, timezone
    
    def process_project(project, company, creator):
        def get_project_status(st):
            if st == 'on_hold':
                return 'Z'
            elif st == 'archived':
                return 'F'
            else:
                return 'A'
            
        id =  project.find('id').text
        
        element = ET.Element('Project')
        add_subelement(element, 'id', 'int', id)
        add_subelement(element, 'name', 'text', project.find('name').text)
        add_subelement(element, 'status', 'text', get_project_status(project.find('status').text))
        add_subelement(element, 'creator', 'int', creator)
        add_subelement(element, 'company', 'int', company)
        add_subelement(element, 'creation_date', 'datetime', convert_date( project.find('created-on').text ))
        
        return id, element

    root = ET.Element(ROOT_ELEMENT) 
    users = ET.SubElement(root, USERS_ELEMENT)
    companies = ET.SubElement(root, 'companies', {'type': 'list'})
    projects = ET.SubElement(root, 'projects', {'type': 'list'})
            
    firm = tree.getroot().find('firm')
    account_holder_id = tree.getroot().find('account-holder-id').text
        
    mcid, mcompany, mtimezone = process_company(firm, False)
    companies.append(mcompany)    
    
    for person in firm.find('people').findall('person'):
        id, user = process_user(person, mcid, mtimezone)
        users.append(user)
    
    #now convert the clients
    for client in tree.getroot().find('clients').findall('client'):
        cid, company, timezone  = process_company(client, False)
        companies.append(company)                    
        #the users in company
        for person in client.find('people').findall('person'):
            id, user = process_user(person, cid, timezone)
            users.append(user)

    #now process projects
    for proj in tree.getroot().find('projects').findall('project'):        
        pid, project = process_project(proj, mcid, account_holder_id) 
        
        project_users = ET.SubElement(project, 'users', {'type': 'list'})
        for person in proj.find('participants').findall('person'):
            user_in_project = ET.SubElement(project_users, 'UserInProject')
            add_subelement(user_in_project, 'id', 'int', person.text)
            add_subelement(user_in_project, 'user', 'int', person.text)
            add_subelement(user_in_project, 'project', 'int', pid)
            add_subelement(user_in_project, 'state', 'text', 'a')
            
            permissions = ET.SubElement(user_in_project, 'permissions', {'type': 'list'})
            add_subelement(permissions, 'message', 'text', 'delete')
            add_subelement(permissions, 'todo', 'text', 'delete')
            add_subelement(permissions, 'wikiboard', 'text', 'delete')
            add_subelement(permissions, 'file', 'text', 'delete')
            add_subelement(permissions, 'milestone', 'text', 'delete')
          
        messages = ET.SubElement(project, 'messages', {'type': 'list'})            
        for post in proj.find('posts').findall('post'):
            message = ET.SubElement(messages, 'Message')
            mid = post.find('id').text
            
            add_subelement(message, 'id', 'int', mid)
            add_subelement(message, 'creator', 'int', post.find('author-id').text)
            add_subelement(message, 'project', 'int', pid)
            add_subelement(message, 'creation_date', 'datetime', convert_datetime( post.find('posted-on').text ) )
            add_subelement(message, 'title', 'text', post.find('title').text)
            add_subelement(message, 'body', 'text', post.find('body').text)            
            add_subelement(message, 'initial_message', 'int', mid)
            
            comments = ET.SubElement(message, 'comments', {'type': 'list'})
            for c in post.find('comments').findall('comment'):
                comment = ET.SubElement(comments, 'Message')
                
                add_subelement(comment, 'id', 'int', c.find('id').text)
                add_subelement(comment, 'creator', 'int', c.find('author-id').text)
                add_subelement(comment, 'creation_date', 'datetime', convert_datetime( c.find('created-at').text ) )
                add_subelement(comment, 'project', 'int', pid)
                add_subelement(comment, 'body', 'text', c.find('body').text)
                add_subelement(comment, 'initial_message', 'int', mid)
                                   
        todolists = ET.SubElement(project, 'todo_lists', {'type': 'list'})  
        for tdl in proj.find('todo-lists').findall('todo-list'):
            tdlist = ET.SubElement(todolists, 'ToDoList')
            tdlid = tdl.find('id').text
            num_todos = len( tdl.find('todo-items').findall('todo-item') )
            
            add_subelement(tdlist, 'id', 'int', tdlid)
            add_subelement(tdlist, 'project', 'int', pid)
            add_subelement(tdlist, 'creator', 'int', account_holder_id) 
            add_subelement(tdlist, 'title', 'text', tdl.find('name').text)
            add_subelement(tdlist, 'description', 'text', tdl.find('description').text)
            add_subelement(tdlist, 'number_of_todos', 'int', num_todos)            
            
            todos = ET.SubElement(tdlist, 'todo_items', {'type': 'list'})
            for t in tdl.find('todo-items').findall('todo-item'):
                todo = ET.SubElement(todos, 'ToDo')
                add_subelement(todo, 'id', 'int', t.find('id').text)
                add_subelement(todo, 'creator', 'int', t.find('creator-id').text)
                add_subelement(todo, 'todo_list', 'int', tdlid)
                add_subelement(todo, 'description', 'text', t.find('content').text)
                add_subelement(todo, 'creation_date', 'datetime', convert_datetime( t.find('created-on').text ) )
                if t.find('completed').text == 'true':
                    add_subelement(todo, 'completion_date', 'datetime', convert_datetime(t.find('completed-on').text) )
                if hasattr(t.find('responsible-party-id'), 'text'):
                    add_subelement(todo, 'responsible', 'int', t.find('responsible-party-id').text)
                add_subelement(todo, 'position', 'int', num_todos)
                num_todos -= 1 
                
        milestones = ET.SubElement(project, 'milestones', {'type': 'list'})   
        for m in proj.find('milestones').findall('milestone'):
            milestone = ET.SubElement(milestones, 'Milestone')
            
            add_subelement(milestone, 'id', 'int', post.find('id').text)
            add_subelement(milestone, 'creator', 'int', m.find('creator-id').text)
            add_subelement(milestone, 'project', 'int', pid)
            add_subelement(milestone, 'title', 'text', m.find('title').text)
            add_subelement(milestone, 'creation_date', 'datetime', convert_datetime( m.find('created-on').text ) )
            add_subelement(milestone, 'due_date', 'datetime', convert_date( m.find('deadline').text ) )            
            add_subelement(milestone, 'send_notification_email ', 'bool', m.find('wants-notification').text == 'true')           
            add_subelement(milestone, 'sent_notification  ', 'bool', False)
                             
            #TODO: check if responsible-party-type can be other than person
            if hasattr(m.find('responsible-party-id'), 'text'):  
                add_subelement(milestone, 'responsible', 'int', m.find('responsible-party-id').text)              
            if m.find('completed').text == 'true':
                add_subelement(milestone, 'completion_date', 'datetime', convert_datetime( m.find('completed-on').text ) )                
                
        projects.append(project)
    indent(root)
    
    return root
