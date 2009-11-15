
from south.db import db
from django.db import models
from rancho.user.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'UserProfile'
        db.create_table('user_userprofile', (
            ('id', orm['user.UserProfile:id']),
            ('user', orm['user.UserProfile:user']),
            ('title', orm['user.UserProfile:title']),
            ('company', orm['user.UserProfile:company']),
            ('office', orm['user.UserProfile:office']),
            ('office_phone', orm['user.UserProfile:office_phone']),
            ('office_phone_ext', orm['user.UserProfile:office_phone_ext']),
            ('mobile_phone', orm['user.UserProfile:mobile_phone']),
            ('home_phone', orm['user.UserProfile:home_phone']),
            ('im_name', orm['user.UserProfile:im_name']),
            ('im_service', orm['user.UserProfile:im_service']),
            ('small_photo', orm['user.UserProfile:small_photo']),
            ('large_photo', orm['user.UserProfile:large_photo']),
            ('mailing_address', orm['user.UserProfile:mailing_address']),
            ('webpage', orm['user.UserProfile:webpage']),
            ('language', orm['user.UserProfile:language']),
            ('timezone', orm['user.UserProfile:timezone']),
            ('is_account_owner', orm['user.UserProfile:is_account_owner']),
        ))
        db.send_create_signal('user', ['UserProfile'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'UserProfile'
        db.delete_table('user_userprofile')
        
    
    
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
        'user.userprofile': {
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['company.Company']", 'null': 'True'}),
            'home_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'im_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'im_service': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'is_account_owner': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en-us'", 'max_length': '10'}),
            'large_photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mailing_address': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'mobile_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'office': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'office_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'office_phone_ext': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True'}),
            'small_photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'timezone': ('TimeZoneField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'webpage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'})
        }
    }
    
    complete_apps = ['user']
