import odoo
import logging
import inspect

from odoo.tools.func import lazy_property
from odoo.http import FilesystemSessionStore
from odoo.http import SESSION_LIFETIME
from odoo.http import Session
from odoo.tools import config

from .session import RedisSessionStore

_logger = logging.getLogger(__name__)

@lazy_property
def session_store(self):

    if config.get('redis_session'):
        host = config.get('redis_host') or 'localhost'
        port = config.get('redis_port') or 6379
        expire = config.get('redis_expire') or SESSION_LIFETIME
        db = config.get('redis_db') or 0
        return RedisSessionStore(session_class=Session,
                                          host=host,
                                          port=port,
                                          expire=int(expire),
                                          db=db
                                          )
    else:
        path = odoo.tools.config.session_dir
        _logger.debug('HTTP sessions stored in: %s', path)
        return FilesystemSessionStore(path, session_class=Session, renew_missing=True)

odoo.http.Application.session_store = session_store