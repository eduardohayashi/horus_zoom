
import redis
import json
from datetime import datetime
from pythontools.verbose import *
import settings

class Redis(object):

    def __init__(self):
        verbose('INIT REDIS', {'host':settings.redis_host,
            'port':settings.redis_port, 'db':settings.redis_db,
            'password':settings.redis_pass}, level=2)
        self.redis = redis.StrictRedis(host=settings.redis_host,
            port=settings.redis_port, db=settings.redis_db,
            password=settings.redis_pass)


    def flush(self):
        self.redis.flushdb()

    def insert_ad(self, id, store, data):
        try:
            key = f'{id}_{store}'
            self.redis.set(name=key, value=json.dumps(data), ex=settings.redis_ttl)
            verbose(key, level=2, label='INFO')
        except:
            verbose('Error trying to set Redis key', key, {'host':settings.redis_host,
                'port':settings.redis_port, 'db':settings.redis_db,
                'password':settings.redis_pass}, label='ERROR')
