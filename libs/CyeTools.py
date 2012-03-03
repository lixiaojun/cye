# -*- coding: utf-8 -*-
'''
Created on 2011-11-20

@author: lixiaojun
'''

from scrapy.conf import settings
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import mapper, relationship, scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import MetaData, Table
from sqlalchemy.types import *
from twisted.enterprise import adbapi
import MySQLdb
import datetime
import redis
import threading
import time

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

'''
New Connect database
'''                               
                             

NOW = time.strftime('%Y-%m-%d %X', time.localtime())

def tostring(dt):
    if isinstance(dt, datetime.datetime):
        return dt.strftime('%Y-%m-%d %X')
    else:
        return dt

_con_str = "mysql://root:wishlist2012@localhost:3306/mygift?charset=utf8"
dbObj = create_engine(_con_str, echo=False)

metadata = MetaData(dbObj)

#Base = declarative_base()
product_tb = Table('product', metadata, autoload=True)
product_price_tb = Table('product_price', metadata, autoload=True)

class ProductPriceObj(object):
    def _to_dict(self):
        _dict = {}
        key_list = ['update_time', 'price']
        for key in key_list:
            if key in self.__dict__.keys():
                _dict[key] = tostring(self.__dict__[key])
        return _dict
    
    def __repr__(self):
        return "%s(%r, %r, %r, %r)" % (self.__class__.__name__, self.id, self.product_pkey, self.price, self.update_time)
    
class ProductObj(object):
    def _to_dict(self):
        _dict = {}
        for key in self.__dict__.keys():
            if key.find('_') >= 0:
                continue
            else:
                _dict[key] = self.__dict__[key] 
        price_key = 'history_price'
        if price_key in dir(self):
            _dict[price_key] = []
            for one in self.history_price:
                _dict[price_key].append(one._to_dict())
        return _dict
    
    def __repr__(self):
        return "%s(%r, %r, %r, %r)" % (self.__class__.__name__, self.pkey, self.title, self.name, self.update_time)
    
mapper(ProductObj, product_tb, properties={'history_price' : relationship(ProductPriceObj)})
#mapper(ProductObj, product_tb)
mapper(ProductPriceObj, product_price_tb)

MygiftSession = sessionmaker(dbObj, autocommit=True)

if __name__ =="__main__":
    session = scoped_session(MygiftSession)
    query = session.query(ProductObj.url)
    results = query.filter("last_crawl_time>DATE_SUB(NOW(), INTERVAL 2 HOUR)").limit(1000).all()
    for url, in results:
        print url
    print len(results)