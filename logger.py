import logging
from flask.logging import default_handler

def get_logger(name):
    log = logging.getLogger(name)
    log.addHandler(default_handler)
    log.setLevel(logging.WARNING)

    return log