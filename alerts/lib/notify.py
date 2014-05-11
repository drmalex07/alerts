import os
import sys
import logging
import Queue as queue
from collections import namedtuple

import lib
from lib.mailer import Mailer

Message = namedtuple('Message', ['title', 'summary', 'message'], verbose=False)

class Notifier(object):

    def __init__(self, name):
        self.name = name
        self.messages = queue.PriorityQueue()
        h1 = logging.StreamHandler()
        h1.setFormatter(logging.Formatter('[%(levelname)-4.4s] [%(name)s] %(message)s'))
        self.log1 = logging.Logger(self.name)
        self.log1.addHandler(h1)
        return

    def add_message(self, msg, priority=0):
        assert isinstance(msg, Message), 'Expected an argument of type %s' %(Message)
        self.messages.put((priority, msg))
        return

    def notify(self):
        n = self.messages.qsize()
        if not n:
            return
        self.log1.info('Notifying on %d events' %(n))
        while not self.messages.empty():
            priority, msg = self.messages.get()
            self.log1.warn("%s: %s" %(msg.title, msg.summary))

class MailNotifier(Notifier):

    MAX_NUM_EMAILS = 1

    def __init__(self, name, recipients, mailer):
        assert isinstance(mailer,Mailer), 'Expected a 2nd argument of type %s' %(Mailer)
        self.recipients = recipients
        self.mailer = mailer
        Notifier.__init__(self, name)
        return

    def notify(self):
        n = self.messages.qsize()
        if not n:
            return
        self.log1.info('Sending email notifications on %d events' %(n))
        i = 0
        while not self.messages.empty():
            priority, msg = self.messages.get()
            self.log1.warn("%s: %s" %(msg.title, msg.summary))
            if i < self.MAX_NUM_EMAILS:
                headers = {
                    'Subject': unicode(msg.title),
                }
                self.mailer.send(self.recipients, headers, msg.message)
                i += 1
        if n > self.MAX_NUM_EMAILS:
            self.log1.warn('Encountered too many email notifications (silenced %d of them)' %(n - self.MAX_NUM_EMAILS))
        return

