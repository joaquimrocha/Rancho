from django.db.models import signals

from rancho.company import models as company_app
from rancho.company.models import Company
from django.contrib.auth.models import User
from rancho.user.models import UserProfile


def create_data(app, created_models, verbosity, **kwargs):
    c = Company()
    c.short_name = "Company"
    c.long_name = "My Company Name"
    c.main_company = True
    c.save()
    
    print "Created initial company"
    
    try:
        user = User.objects.get(id=1)    
        up = UserProfile()
        up.is_account_owner = True
        up.user = user         
        up.company = c  
        up.save()
        
        print "Created initial profile"
    except:
        pass


signals.post_syncdb.connect(create_data, sender=company_app)

