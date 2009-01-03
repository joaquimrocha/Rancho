from django.db import models
from rancho.django_evolution.mutations import DeleteModel, AddField, \
    SQLMutation
from rancho.todo.models import ToDoList

#FIXME: maybe this is not an ideal solution either
def initial_todo_list_value():
    todo_list_objects = ToDoList.objects.all()
    if todo_list_objects:
        return todo_list_objects[0].id
    return 0

MUTATIONS = [
    #FIXME: this shouldn't be null but it's the only way to make this work, maybe we can change it after
    AddField('ToDo', 'todo_list', models.ForeignKey, null=True, initial=initial_todo_list_value, related_model='todo.ToDoList'),
    AddField('ToDo', 'position', models.IntegerField, initial=0),
    SQLMutation('update data', ["UPDATE todo_todo SET todo_list_id=(SELECT todolist_id FROM todo_todo_in_todolist WHERE todo_id=todo_todo.id);"]),
    DeleteModel('ToDo_in_ToDoList'),
]

