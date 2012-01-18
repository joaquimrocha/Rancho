from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group
from django.db.models import Q
import new
import inspect

class MetaClass(type):
    def __new__(self, classname, classbases, classdict):
        try:
            frame = inspect.currentframe()
            frame = frame.f_back
            if frame.f_locals.has_key(classname):
                old_class = frame.f_locals.get(classname)
                for name,func in classdict.items():
                    if inspect.isfunction(func):
                        setattr(old_class, name, func)
                return old_class
            return type.__new__(self, classname, classbases, classdict)
        finally:
            del frame

class MetaObject(object):
    __metaclass__ = MetaClass

class User(MetaObject):

    def add_row_perm(self, instance, perm):
        from models import Permission

        if self.has_row_perm(instance, perm, True):
            return False
        permission = Permission()
        permission.content_object = instance
        permission.user = self
        permission.name = perm
        permission.save()
        return True

    def del_row_perm(self, instance, perm):
        from models import Permission

        if not self.has_row_perm(instance, perm, True):
            return False
        content_type = ContentType.objects.get_for_model(instance)
        objects = Permission.objects.filter(user=self, content_type__pk=content_type.id, object_id=instance.id, name=perm)
        objects.delete()
        return True

    def has_row_perm(self, instance, perm, only_me=False):
        from models import Permission

        if self.is_superuser:
            return True
        if not self.is_active:
            return False

        content_type = ContentType.objects.get_for_model(instance)
        objects = Permission.objects.filter(user=self, content_type__pk=content_type.id, object_id=instance.id, name=perm)
        if objects.count()>0:
            return True

        # check groups
        if not only_me:
            for group in self.groups.all():
                if group.has_row_perm(instance, perm):
                    return True
        return False

    def get_rows_with_permission(self, instance, perm):
        from models import Permission

        content_type = ContentType.objects.get_for_model(instance)
        objects = Permission.objects.filter(Q(user=self) | Q(group__in=self.groups.all()), content_type__pk=content_type.id, name=perm)
        return objects

    def clean_permissions(self, instance):
        from models import Permission

        content_type = ContentType.objects.get_for_model(instance)
        Permission.objects.filter(Q(user=self) | Q(group__in=self.groups.all()), content_type__pk=content_type.id).delete()

class Group(MetaObject):
    def add_row_perm(self, instance, perm):
        from models import Permission

        if self.has_row_perm(instance, perm):
            return False
        permission = Permission()
        permission.content_object = instance
        permission.group = self
        permission.name = perm
        permission.save()
        return True

    def del_row_perm(self, instance, perm):
        from models import Permission

        if not self.has_row_perm(instance, perm):
            return False
        content_type = ContentType.objects.get_for_model(instance)
        objects = Permission.objects.filter(user=self, content_type__pk=content_type.id, object_id=instance.id, name=perm)
        objects.delete()
        return True

    def has_row_perm(self, instance, perm):
        from models import Permission

        content_type = ContentType.objects.get_for_model(instance)
        objects = Permission.objects.filter(group=self, content_type__pk=content_type.id, object_id=instance.id, name=perm)
        if objects.count()>0:
            return True
        else:
            return False

    def get_rows_with_permission(self, instance, perm):
        from models import Permission

        content_type = ContentType.objects.get_for_model(instance)
        objects = Permission.objects.filter(group=self, content_type__pk=contet_type.id, name=perm)
        return objects


def get_users_with_permission(instance, perm):
    """
    gets all the users with have a given permission on a given project
    """

    from models import Permission

    content_type = ContentType.objects.get_for_model(instance)
    objects = Permission.objects.filter(object_id=instance.id, content_type__pk=content_type.id, name=perm).values_list('user', flat=True)
    users = User.objects.filter(is_active=True, id__in=objects)
    return users
