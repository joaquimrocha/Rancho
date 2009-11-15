#!/bin/sh

svn co -r 46 http://django-pagination.googlecode.com/svn/trunk/pagination pagination
svn co -r 154 http://django-tagging.googlecode.com/svn/trunk/tagging/ tagging
svn co -r 49 http://django-mailer.googlecode.com/svn/trunk/mailer/ mailer
svn co -r 60 http://django-tinymce.googlecode.com/svn/trunk/tinymce/ tinymce
svn co -r 35 http://django-timezones.googlecode.com/svn/trunk/timezones/ timezones
svn co -r 125 http://django-notification.googlecode.com/svn/trunk/notification notification
svn co -r 348 http://svn.whoosh.ca/projects/whoosh/trunk/src/whoosh/ whoosh

#get django-haystack
git clone git://github.com/toastdriven/django-haystack.git 
mv django-haystack/haystack haystack
rm -rf django-haystack
