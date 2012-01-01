'''
Created on 2011-10-18

@author: lixiaojun
'''
# test by pipeline
from libs.pytesser.pytesser import image_to_string
from scrapy import log, signals
from scrapy.conf import settings
from scrapy.contrib.pipeline.images import ImagesPipeline, ImageException
from scrapy.exceptions import DropItem, DropItem, NotConfigured
from scrapy.http import Request
from scrapy.utils.serialize import ScrapyJSONEncoder
from scrapy.xlib.pydispatch import dispatcher
from twisted.internet.threads import deferToThread
import Image
import StringIO
import json
import redis

IMAGES_STORE = settings.get('IMAGES_STORE')

class JsonWritePipeline(object):
    def __init__(self):
        self.duplicates = {}
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.file = open('product.jl', 'wb')
        
    def process_item(self, item, spider):
        if item['pkey'] in self.duplicates[spider]:
            raise DropItem("Duplicate item found: %s", item['title'])
        else:
            self.duplicates[spider].add(item['pkey'])
            line = json.dumps(dict(item))+"\n"
            self.file.write(line)
            return item
    
    def spider_opened(self, spider):
        self.duplicates[spider] = set()
    
    def spider_closed(self, spider):
        del self.duplicates[spider]
    pass



class CyePriceImagesPipeline(ImagesPipeline):
    
    def __init__(self, store_uri, download_func=None):
        super(CyePriceImagesPipeline, self).__init__(store_uri, download_func=download_func)
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.file = open('price.jl', 'wb')
    
    
    @classmethod
    def from_settings(cls, settings):
        cls.MIN_WIDTH = settings.getint('IMAGES_MIN_WIDTH', 0)
        cls.MIN_HEIGHT = settings.getint('IMAGES_MIN_HEIGHT', 0)
        cls.EXPIRES = settings.getint('IMAGES_EXPIRES', 90)
        cls.THUMBS = {}
        s3store = cls.STORE_SCHEMES['s3']
        s3store.AWS_ACCESS_KEY_ID = settings['AWS_ACCESS_KEY_ID']
        s3store.AWS_SECRET_ACCESS_KEY = settings['AWS_SECRET_ACCESS_KEY']
        store_uri = settings['IMAGES_STORE']
        return cls(store_uri)
    
    def image_key(self, url):        
        filename = url.split('/')[-1]        
        return 'price/%s' % (filename)
    
    def get_media_requests(self, item, info):
        if item['price_image_url'] is not None:
            image_url = item['price_image_url']
            return [Request(image_url)]
    
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        for image_path in image_paths:
            full_path = IMAGES_STORE +'/'+image_path
            im = Image.open(full_path)
            text = image_to_string(im)
            item['product_price'] = text[2:].strip()
        line = json.dumps(dict(item))+"\n"
        self.file.write(line)
        return item
        
    def spider_opened(self, spider):
        self.duplicates[spider] = set()
    
    def spider_closed(self, spider):
        del self.duplicates[spider]

    def handle_error(self,e):
        log.err(e)
        


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