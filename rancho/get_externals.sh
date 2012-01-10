#!/bin/sh

URLS="git://github.com/jtauber/django-notification.git
      git://github.com/jtauber/django-mailer.git
      https://github.com/ericflo/django-pagination.git
      https://github.com/brosner/django-tagging.git
      https://github.com/aljosa/django-tinymce.git
      https://github.com/brosner/django-timezones.git"

for giturl in $URLS; do
    projectname=`echo $giturl | sed 's/.*\(django\-.*\)\.git/\1/'`
    modulename=`echo $projectname | sed 's/.*django\-\(.*\)$/\1/'`
    git clone $giturl
    mv $projectname/$modulename .
    rm -rf $projectname
done

git clone git://github.com/toastdriven/django-haystack.git
cd django-haystack && git checkout v1.2.6; cd ..
mv django-haystack/haystack .
rm -rf django-haystack

hg clone https://bitbucket.org/mchaput/whoosh whoosh.repo
mv whoosh.repo/src/whoosh .
rm -rf whoosh.repo
