# -*- coding: utf-8 -*-
'''
Created on 2011-11-20

@author: lixiaojun
'''

import redis
import threading



class CyeRedis(object):
    
    __inst = None
    __lock = threading.Lock()
    
    HOST = "localhost"
    PORT = 6379
    DB = 0
    PWD = 'hello1234'
    
    def __init__(self, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        self.redis_conn = redis.Redis(host=self.HOST, port=self.PORT, db=self.DB, password=self.PWD)
    
        
    @staticmethod
    def getInstance():
        CyeRedis.__lock.acquire()
        if not CyeRedis.__inst:
            CyeRedis.__inst = CyeRedis()
        CyeRedis.__lock.release()
        return CyeRedis.__inst.redis_conn
