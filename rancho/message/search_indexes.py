from haystack import indexes, site
from rancho.message.models import Message

class MessageIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    project = indexes.IntegerField(model_attr='project', use_template=True)
    user = indexes.CharField(model_attr='creator')
site.register(Message, MessageIndex)
