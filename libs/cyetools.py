# -*- coding: utf-8 -*-
'''
Created on 2011-11-20

@author: lixiaojun
'''

from scrapy.conf import settings
import redis
import threading

# default values
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PWD = 'hello1234'

class CyeRedis(object):
    
    __inst = None
    __lock = threading.Lock()
    
    def __init__(self, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        #TODO get setting for settings.conf
        host = settings.get('REDIS_HOST', REDIS_HOST)
        port = settings.get('REDIS_PORT', REDIS_PORT)
        db = settings.get('REDIS_DB', REDIS_DB)
        pwd = settings.get('REDIS_PWD', REDIS_PWD)
        self.redis_conn = redis.Redis(host=host, port=port, db=db, password=pwd)
        
    
        
    @staticmethod
    def getInstance():
        CyeRedis.__lock.acquire()
        if not CyeRedis.__inst:
            CyeRedis.__inst = CyeRedis()
        CyeRedis.__lock.release()
        return CyeRedis.__inst.redis_conn
