import redis
import logging
import pickle

from odoo.service.security import compute_session_token
from odoo.tools._vendor.sessions import SessionStore


_logger = logging.getLogger(__name__)

# Class to drop in place of filesystemsessionstore
class RedisSessionStore(SessionStore):

    # Custom init to get additional data for redis connection
    def __init__(self, host, port, expire, db, session_class=None, key_template='session_%s'):

        super(RedisSessionStore, self).__init__(session_class=session_class)

        self.port = port
        self.host = host
        self.db = db
        self.key_template = key_template
        self.expire = expire
        self.redis = self._redisConnect()

    # connect to the redis db or be angry
    def _redisConnect(self):
        try:
            redisObject = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
            )
            redisObject.ping()
            _logger.debug('Connection to the redis db was successful')
            return redisObject
        except Exception as e:
            _logger.error('Cannot contact redis db : %r', e)
            return False
    
    def _renameSessionKey(self, sid):
        return (self.key_template % sid)

    # set data in redis with a key and expiration
    def save(self, session):
        try:
            session_key = self._renameSessionKey(session.sid)
            return self.redis.set(
                session_key, pickle.dumps(
                    dict(session)), ex=self.expire)
        except Exception as e:
            _logger.debug('%r', e)

    def get(self, sid):
        try:
            session_key = self._renameSessionKey(sid)
            data = self.redis.get(session_key)
            self.redis.set(session_key, data, ex=self.expire)
            data = pickle.loads(data)
        except BaseException:
            data = {}
        return self.session_class(data, sid, False)

    # Direct copy of filesystem version
    def rotate(self, session, env):
        self.delete(session)
        session.sid = self.generate_key()
        if session.uid and env:
            session.session_token = compute_session_token(session, env)
        self.save(session)

    # API for session store
    def delete(self, session):
        try:
            self.redis.delete(session.sid)
        except Exception as e:
            _logger.debug('%r', e)

    # Vacuum is unnecessary in redis
    # we set an expire to SESSION_LIFETIME on the value
    def vacuum(self):
        return

    def list(self):
        keys = self.redis.keys('*')
        return [key[len(self.prefix):] for key in keys]