import logging
import zope.interface

from alerts.lib.interfaces import IChecker, INotifier

class Checker(object):
    
    zope.interface.implements(IChecker)

    def __init__(self, notifier):
        self._log = logging.getLogger(__name__)
        self._notifier = notifier
        self._data_dir = None
        self._opts = None
        self._log.info('Created instance')
        pass

    def configure(self, data_dir, opts):
        self._data_dir = data_dir
        self._opts = opts.copy()
        self._log.info(
            'Configured instance with: data_dir=%s opts=%r' % (data_dir, opts))
        pass
    
    def check(self, hostname):
        self._log.info('Checking host: %s', hostname)
        pass

