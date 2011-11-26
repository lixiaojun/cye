'''
Created on 2011-10-18

@author: lixiaojun
'''
# test by pipeline
import json
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.exceptions import DropItem

class JsonWritePipeline(object):
    def __init__(self):
        self.duplicates = {}
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.file = open('items.jl', 'wb')
        
    def process_item(self, item, spider):
        if item['queue_key'] in self.duplicates[spider]:
            raise DropItem("Duplicate item found: %s", item['title'])
        else:
            self.duplicates[spider].add(item['queue_key'])
            line = json.dumps(dict(item))+"\n"
            self.file.write(line)
            return item
    
    def spider_opened(self, spider):
        self.duplicates[spider] = set()
    
    def spider_closed(self, spider):
        del self.duplicates[spider]
    pass


import redis

from twisted.internet.threads import deferToThread
from scrapy.utils.serialize import ScrapyJSONEncoder


class RedisPipeline(object):
    """Pushes serialized item into a redis list/queue"""

    def __init__(self, host, port):
        self.server = redis.Redis(host, port)
        self.encoder = ScrapyJSONEncoder()

    @classmethod
    def from_settings(cls, settings):
        host = settings.get('REDIS_HOST', 'localhost')
        port = settings.get('REDIS_PORT', 6379)
        return cls(host, port)

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        key = self.item_key(item, spider)
        data = self.encoder.encode(dict(item))
        self.server.rpush(key, data)
        return item

    def item_key(self, item, spider):
        """Returns redis key based on given spider"""
        return "%s:items" % spider.name