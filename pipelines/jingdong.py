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
from twisted.enterprise import reflector
import Image
import datetime
import hashlib
import json
import os
import time

PRICE_IMAGES_STORE = settings.get('IMAGES_STORE')
TIME_FORMAT = "%Y-%m-%d %X"
UPDATE_DETAIL_TIEM_INTERVAL = settings.get('UPDATE_DETAIL_TIEM_INTERVAL')

"""
get delta value of two time
"""
def DeltaTime(newtime, oldtime, mformat = TIME_FORMAT):
    newtime = time.strptime(newtime, mformat)
    oldtime = time.strptime(oldtime, mformat)
    
    ndate = datetime.datetime(newtime[0], newtime[1], newtime[2])
    odate = datetime.datetime(oldtime[0], oldtime[1], oldtime[2])
    return (ndate - odate).days
    
"""
To test
"""
class JsonWritePipeline(object):
    def __init__(self):
        self.file = open('item.jl', 'wb')
        
    def process_item(self, item, spider):
        line = json.dumps(dict(item))+"\n"
        self.file.write(line)
        return item
            
    pass

"""
Initialize Product Info
To decide whether to update the product information 
"""
class CyeFirstPipeline(object):
    def __init__(self):
        self.file = open('first.jl', 'wb')
        
    def process_item(self, item, spider):
        line = json.dumps(dict(item))+"\n"
        self.file.write(line)
        return item
    
    def getInfo(self, pkey, item):
        if pkey is None:
            def _callback_set_status(self, datas):
                if datas:
                    data = datas[0]
                    if DeltaTime(data.update_time, item['crawl_time']) < UPDATE_DETAIL_TIEM_INTERVAL:
                        item['is_update_detail'] = False
                        
            def _callback_set_price(self, datas):
                if datas:
                    data = datas[0]
                    if data.price:
                        item['price'] = data.price
            d = ProductReflector.loadObjectsFrom("product",
                                                 whereClause=[("pkey", reflector.EQUAL, pkey)])
            d.addcallback(_callback_set_status)
            
            
    pass


"""
Data writing database
"""
class CyeToDBPipeline(object):
    def __init__(self):
        self.prow = ProductRow()
        self.file = open('todb.jl', 'wb')
        
    def process_item(self, item, spider):
        self.item2Row(item, self.prow)
        self.handle_detail(item, spider, self.prow)
        line = json.dumps(dict(self.prow.__dict__))+"\n"
        self.file.write(line)
        return item 
    
    def handle_detail(self, item, spider, row):
        if hasattr(item, 'detail') and item['detail'] is not None:
            myfilter = getattr(CyeFilter, CyeFilter.getFilterClassName(spider.namespace))
            detail_dict = myfilter.handleDetail(item['detail'])
            myfilter.detail2Model(detail_dict, row)
    
    def item2Row(self, item, row):
        row.assignKeyAttr('id', 0)
        item_keys = item.fields.keys()
        rowkey_attrs = [ attr for attr, t in row.rowKeyColumns ]
        for attr, value in  row.rowColumns:
            if attr in item_keys:
                if attr in rowkey_attrs:
                    row.assignKeyAttr(attr, item[attr])
                else:
                    setattr(row, attr, item[attr])    
    pass


"""
Download price's image and Processing price information
"""
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
        
"""
Download Product's image
"""       
class CyeProductImagesPipeline(ImagesPipeline):
    
    def __init__(self, store_uri, download_func=None):
        super(CyeProductImagesPipeline, self).__init__(store_uri, download_func=download_func)
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
    
    def image_key(self, url):
        image_guid = hashlib.sha1(url).hexdigest()
        return 'images/full/%s.jpg' % (image_guid)

    def thumb_key(self, url, thumb_id):
        image_guid = hashlib.sha1(url).hexdigest()
        return 'images/thumbs/%s/%s.jpg' % (thumb_id, image_guid)

    def handle_error(self,e):
        log.err(e)
