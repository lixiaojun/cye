# -*- coding: utf-8 -*-
'''
Created on 2011-11-20

@author: lixiaojun
'''

from scrapy.conf import settings
from twisted.enterprise import adbapi
import MySQLdb
import redis
import threading

# default values
redisdbconf = settings.get('REDISDB_CONF')
REDIS_HOST = redisdbconf.get('host', 'localhost')
REDIS_PORT = redisdbconf.get('port', 6379)
REDIS_DB = redisdbconf.get('db', 0)
REDIS_PWD = redisdbconf.get('passwd', 'hello1234')

class CyeRedis(object):
    
    __inst = None
    __lock = threading.Lock()
    
    def __init__(self, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        self.redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PWD)
        
    
        
    @staticmethod
    def getInstance():
        CyeRedis.__lock.acquire()
        if not CyeRedis.__inst:
            CyeRedis.__inst = CyeRedis()
        CyeRedis.__lock.release()
        return CyeRedis.__inst.redis_conn
    
    
'''
Connect database
'''
mysqldbconf = settings.get('MYSQLDB_CONF')

DB_PORT   = mysqldbconf.get('port', 3306)
DB_USER   = mysqldbconf.get('user', 'root')
DB_HOST   = mysqldbconf.get('host', 'localhost')
DB_PASSWD = mysqldbconf.get('passwd', '123456')


CyeGiftDBpool = adbapi.ConnectionPool("MySQLdb", host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWD, \
                                   db='mygift',use_unicode=True, charset='utf8', read_default_file='/etc/mysql/my.cnf')

CyeGiftCursor = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWD, \
                                  db='mygift',use_unicode=True, charset='utf8', read_default_file='/etc/mysql/my.cnf').cursor()
'''
CyeDBpool = adbapi.ConnectionPool('MySQLdb', host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWD, \
                                  db='cye_db',use_unicode=True, charset='utf8', read_default_file='/etc/mysql/my.cnf')

CyeCursor = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWD, \
                                  db='cye_db',use_unicode=True, charset='utf8', read_default_file='/etc/mysql/my.cnf').cursor()
'''