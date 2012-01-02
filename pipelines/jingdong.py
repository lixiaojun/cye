'''
Created on 2011-10-18

@author: lixiaojun
'''
# test by pipeline
from libs import CyeFilter
from libs.CyeModels import ProductReflector, ProductRow
from libs.pytesser.pytesser import image_to_string
from scrapy import log, signals
from scrapy.conf import settings
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
import Image
import json
import os

PRICE_IMAGES_STORE = settings.get('IMAGES_STORE')
PRODUCT_IMAGES_STORE = settings.get('IMAGES_STORE')+'/product'

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

class CyeProductPipeline(object):
    def __init__(self):
        self.prow = ProductRow()
        
    def process_item(self, item, spider):
        self.item2Row(item, self.prow)
        self.handle_detail(item, spider, self.prow)
        return item 
    
    def handle_detail(self, item, spider, row):
        if item['detail'] is not None:
            filter = getattr(CyeFilter, CyeFilter.getFilterClassName(spider.namespace))
            detail_dict = filter.handleDetail(item['detail'])
            filter.detail2Model(detail_dict, row)
    
    def item2Row(self, item, row):
        for attr, value in  row.rowColumns:
            if hasattr(item, attr):
                row[attr] = item[attr]
            
    pass



class CyePriceImagesPipeline(ImagesPipeline):
    
    def __init__(self, store_uri, download_func=None):
        super(CyePriceImagesPipeline, self).__init__(store_uri, download_func=download_func)
        
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
        if not image_paths:
            raise DropItem("Item contains no images")
        for image_path in image_paths:
            full_path = PRICE_IMAGES_STORE +'/'+image_path
            im = Image.open(full_path)
            text = image_to_string(im)
            item['price'] = text[2:].strip()
        line = json.dumps(dict(item))+"\n"
        self.file.write(line)
        return item

    def handle_error(self,e):
        log.err(e)
        
class CyeProductImagesPipeline(ImagesPipeline):
    
    def __init__(self):
        self.file = open('product_image.jl', 'wb')
    
    def get_media_requests(self, item, info):
        if item['origin_image_url'] is not None:
            image_url = item['origin_image_url']
            return [Request(image_url)]
    
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        for image_path in image_paths:
            item['image'] = os.path.basename(image_path.strip())
            break
        line = json.dumps(dict(item))+"\n"
        self.file.write(line)
        return item
    
    
        
    def spider_opened(self, spider):
        self.duplicates[spider] = set()
    
    def spider_closed(self, spider):
        del self.duplicates[spider]

    def handle_error(self,e):
        log.err(e)
