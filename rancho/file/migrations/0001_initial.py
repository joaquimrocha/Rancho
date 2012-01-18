
from south.db import db
from django.db import models
from rancho.file.models import *

class Migration:

    def forwards(self, orm):

        # Adding model 'File'
        db.create_table('file_file', (
            ('id', orm['file.File:id']),
            ('creator', orm['file.File:creator']),
            ('project', orm['file.File:project']),
            ('title', orm['file.File:title']),
            ('last_file_version', orm['file.File:last_file_version']),
            ('tags', orm['file.File:tags']),
        ))
        db.send_create_signal('file', ['File'])

        # Adding model 'FileVersion'
        db.create_table('file_fileversion', (
            ('id', orm['file.FileVersion:id']),
            ('file', orm['file.FileVersion:file']),
            ('file_location', orm['file.FileVersion:file_location']),
            ('file_size', orm['file.FileVersion:file_size']),
            ('creation_date', orm['file.FileVersion:creation_date']),
            ('description', orm['file.FileVersion:description']),
            ('creator', orm['file.FileVersion:creator']),
            ('file_type', orm['file.FileVersion:file_type']),
        ))
        db.send_create_signal('file', ['FileVersion'])

        # Adding ManyToManyField 'File.notify_to'
        db.create_table('file_file_notify_to', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('file', models.ForeignKey(orm.File, null=False)),
            ('user', models.ForeignKey(orm['auth.User'], null=False))
        ))



    def backwards(self, orm):

        # Deleting model 'File'
        db.delete_table('file_file')

        # Deleting model 'FileVersion'
        db.delete_table('file_fileversion')

        # Dropping ManyToManyField 'File.notify_to'
        db.delete_table('file_file_notify_to')



    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'company.company': {
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'display_logo_name': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'mailing_address': ('django.db.models.fields.TextField', [], {'max_length': '500', 'null': 'True'}),
            'main_company': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'webpage': ('django.db.models.fields.URLField', [], {'max_length': '500', 'null': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'file.file': {
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_file_version': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lastversion'", 'null': 'True', 'to': "orm['file.FileVersion']"}),
            'notify_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'tags': ('TagField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'file.fileversion': {
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'uploader'", 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['file.File']"}),
            'file_location': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'file_size': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'file_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'project.project': {
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['company.Company']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'creator'", 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'finish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['file']
