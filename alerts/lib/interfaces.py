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

class IChecker(Interface):

    def configure(data_dir, opts):
        '''Configure this checker from the running environment.'''
        pass
    
    def check(hostname):
        '''Perform checks on the specified host, generate alerts if needed.'''
        pass

