from django.contrib.auth.models import User
from django.db.models import signals
from rancho.company import models as company_app
from rancho.company.models import Company
from rancho.user.models import UserProfile



def create_data(app, created_models, verbosity, **kwargs):
    
    c, val = Company.objects.get_or_create(main_company = True)
    if val:
        c.short_name = "Company"
        c.long_name = "My Company Name"
        c.save()
        print "Created initial Company successfully."
    
    try:
        user = User.objects.get(id=1)
        up, val = UserProfile.objects.get_or_create(is_account_owner = True, user = user, company = c)    
        if val:        
            print "Created initial profile successfully."
    except:
        pass


signals.post_syncdb.connect(create_data, sender=company_app)

