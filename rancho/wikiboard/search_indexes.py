from haystack import indexes, site
from rancho.wikiboard.models import WikiEntry

class WikiEntryIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    project = indexes.IntegerField(model_attr='project', use_template=True)
    user = indexes.CharField(model_attr='author')
site.register(WikiEntry, WikiEntryIndex)
