import os
import logging
import genshi.template
from ConfigParser import ConfigParser

config = {}

template_dirs = []
template_loader = genshi.template.TemplateLoader()

from .class_loader import load_class

def config_from_file(config_file):
    global config
    global template_dirs
    global template_loader
    
    # Read configuration

    here = os.path.abspath('.')

    confp = ConfigParser(defaults={'here': here})
    confp.read(config_file)
    
    for sec in ('stats', 'checkers', 'alerts', 'mailer'):
        config[sec] = dict(confp.items(sec))

    # Setup template loader

    template_dirs = [
        os.path.abspath('./templates')]
    template_loader.search_path.extend(template_dirs)
    
    # Load and register additional checkers
    
    for name, cls_name in confp.items('checkers'):
        if name != 'here':
            cls = _load_checker(name, cls_name)
            logging.info('Loaded checker %s: %r', name, cls)

    return

def _load_checker(name, cls_name):
    from alerts.lib.checkers import named_checker
    
    cls = load_class(cls_name)
    return named_checker(name)(cls)
