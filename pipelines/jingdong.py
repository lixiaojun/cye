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
        if item['url'] in self.duplicates[spider]:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.duplicates[spider].add(item['url'])
            line = json.dumps(dict(item))+"\n"
            self.file.write(line)
            return item
    
    def spider_opened(self, spider):
        self.duplicates[spider] = set()
    
    def spider_closed(self, spider):
        del self.duplicates[spider]
    pass