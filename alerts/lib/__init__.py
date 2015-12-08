import zope.interface
from collections import namedtuple

from .interfaces import ICheckContext

@zope.interface.implementer(ICheckContext)
class CheckContext(namedtuple('_Context', ['name', 'hostname'])):
    
    pass

class Message(namedtuple('_Message', ['title', 'summary', 'body'])): 
    
    def __str__(self):
        return str(self.summary)

    def __unicode__(self):
        if isinstance(self.summary, str):
            return self.summary.decode('utf-8')
        else:
            return unicode(self.summary)
