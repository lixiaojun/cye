# -*- coding: utf-8 -*-
'''
Created on 2011-11-20

@author: lixiaojun
'''

from libs.cyetools import CyeRedis
from scrapy.utils.request import request_fingerprint
from twisted.python import hashlib
import time

class BaseDupeFilter(object):
    
    @classmethod
    def from_settings(cls, settings):
        return cls()
    
    def request_seen(self, request):
        return False
    
    def open(self):  # can return deferred
        pass
    
    def close(self, reason): # can return a deferred
        pass



class RFPDupeFilter(BaseDupeFilter):
    """Redis-based request duplication filter"""

    def __init__(self, redis_cli, key):
        """Initialize duplication filter

        Parameters:
            redis_cli -- Redis connection
            key -- redis key to store fingerprints

        """
        self.redis_cli = redis_cli
        self.key = key

    @classmethod
    def from_settings(cls):
        redis_cli = CyeRedis.getInstance()
        # create one-time key. needed to support to use this
        # class as standalone dupefilter with scrapy's default scheduler
        # if scrapy passes spider on open() method this wouldn't be needed
        key = "dupefilter:%s" % int(time.time())
        return cls(redis_cli, key)

    def request_seen(self, request):
        fp = request_fingerprint(request)
        added = self.redis_cli.sadd(self.key, fp)
        return not added

    def close(self, reason):
        """Delete data on close. Called by scrapy's scheduler"""
        self.clear()

    def clear(self):
        """Clears fingerprints data"""
        self.redis_cli.delete(self.key)

