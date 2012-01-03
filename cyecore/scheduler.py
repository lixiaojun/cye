# -*- coding: utf-8 -*-
'''
Created on 2011-11-19

@author: lixiaojun
'''


from cyecore.dupefilter import RFPDupeFilter
from cyecore.queue import SpiderQueue
from libs.CyeTools import CyeRedis
from scrapy import log

# default values
SCHEDULER_PERSIST = False
QUEUE_KEY = '%(namespace)s:%(spider)s:requests'
DUPEFILTER_KEY = '%(namespace)s:%(spider)s:dupefilter'

class Scheduler(object):
    """Redis-based scheduler"""

    def __init__(self,redis_cli, persist, queue_key):
        self.redis_cli = redis_cli
        self.persist = persist
        self.queue_key = queue_key
        pass
        

    def __len__(self):
        return len(self.queue)
    
    @classmethod
    def from_settings(cls, settings):
        redis_cli = CyeRedis.getInstance()
        persist = settings.get('SCHEDULER_PERSIST', SCHEDULER_PERSIST)
        queue_key = settings.get('SCHEDULER_QUEUE_KEY', QUEUE_KEY)
        return cls(redis_cli, persist, queue_key)

    def open(self, spider):
        self.spider = spider
        self.queue_key = self.get_queue_key(spider)
        self.queue = SpiderQueue(self.redis_cli, spider, self.queue_key)
        self.df = RFPDupeFilter(self.redis_cli, self.get_dupefilter_key(spider))
        if spider is not None:
            spider.log("Queue key of redis (%s)" % self.get_queue_key(spider), log.INFO)
            spider.log("Dupefilter key of redis (%s)" % self.get_dupefilter_key(spider), log.INFO)
            
        # notice if there are requests already in the queue
        if len(self.queue):
            spider.log("Resuming crawl (%d requests scheduled)" % len(self.queue))

    def close(self, reason):
        if not self.persist:
            self.df.clear()
            self.queue.clear()

    def enqueue_request(self, request):
        if not request.dont_filter and self.df.request_seen(request):
            return
        self.queue.push(request)

    def next_request(self):
        return self.queue.pop()

    def has_pending_requests(self):
        return len(self) > 0
    
    def get_queue_key(self, spider):
        """Returns redis dupe key based on given spider"""
        qkey = QUEUE_KEY % {'namespace':spider.namespace, 'spider': spider.name}
        return str(qkey)
    
    def get_dupefilter_key(self, spider):
        """Returns redis dupe key based on given spider"""
        return DUPEFILTER_KEY % {'namespace':spider.namespace, 'spider': spider.name}
