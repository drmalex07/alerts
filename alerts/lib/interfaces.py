import re
import zope.interface
import zope.schema
from zope.interface import Interface
from zope.interface.adapter import AdapterRegistry

adapter_registry = AdapterRegistry()

class INotifier(Interface):

    def add_message(msg, priority):
        '''Enqueue a new message with a given priority.'''
        pass

    def notify():
        '''Pop and send notifications for queued messages.'''
        pass

re_hostname = re.compile(
    '^' + '(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*' + 
    '([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])' + '$')

class ICheckContext(Interface):
    
    name = zope.schema.DottedName(required=False)
    
    hostname = zope.schema.NativeString(required=True, constraint=re_hostname.match)

class IChecker(Interface):

    def setup(collection_dir, logger, opts):
        '''Setup this checker from given configuration.'''
        pass
    
    def data_dir(hostname):
        '''Get the (local) absolute path for collectd stats of a given host.'''
        pass

    def get_logger(hostname):
        '''Get a context-aware logger to handle messages for a given host'''
        pass

    def check(hostname):
        '''Perform checks on the specified host, generate alerts if needed.'''
        pass

