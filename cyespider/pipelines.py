# -*- coding: utf-8 -*-
'''
Created on 2011-10-18

@author: lixiaojun
'''
# test by pipeline
from libs import CyeFilter
from libs.CyeTools import ProductObj, ProductPriceObj
from libs.pytesser.pytesser import image_file_to_string
from scrapy import log, signals
from scrapy.conf import settings
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
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
    
    ndate = datetime.datetime(newtime[0], newtime[1], newtime[2], newtime[3], newtime[4], newtime[5])
    odate = datetime.datetime(oldtime[0], oldtime[1], oldtime[2], oldtime[3], oldtime[4], oldtime[5])
    return (ndate - odate).days

def DeltaSecTime(newtime, oldtime, mformat = TIME_FORMAT):
    newtime = time.strptime(newtime, mformat)
    oldtime = time.strptime(oldtime, mformat)
    
    ndate = datetime.datetime(newtime[0], newtime[1], newtime[2], newtime[3], newtime[4], newtime[5])
    odate = datetime.datetime(oldtime[0], oldtime[1], oldtime[2], oldtime[3], oldtime[4], oldtime[5])
    d1 = time.mktime(ndate.timetuple())
    d2 = time.mktime(odate.timetuple())
    return d1 - d2
    

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

class SessionPipeline(object):
    def __init__(self):
        self.duplicates = {}
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        
    def spider_opened(self, spider):
        pass
        
    def spider_closed(self, spider):
        try:
            spider.session.commit()
            spider.log("%s : Session commit." % self.__class__, log.INFO)
        except:
            spider.session.rollback()
            spider.log("%s : Session rollback." % self.__class__, log.ERROR)
            raise
        finally:
            spider.session.commit()
            
        
    def process_item(self, item, spider):
        return item
        
    

"""
Initialize Product Info
To decide whether to update the product information 
"""
class CyeFirstPipeline(object):
    def __init__(self):
        pass
        
    def process_item(self, item, spider):
        self.setInfo(item, spider)
        return item
    
    def setInfo(self, item, spider):
        if 'pkey' in item.keys() and item['pkey'] is not None:
            self._setItemInfo(item, spider)
            
    def _setItemInfo(self, item, spider):
        pkey = item['pkey']
        item['product_pkey'] = item['pkey']
        item['last_price'] = None
        item['product_id'] = None
        item['product'] = ProductObj()
        
        query = spider.session.query(ProductObj)
        product = query.filter(ProductObj.pkey == pkey).first()
        if product:
            item['product'] = product
            item['product_id'] = product.id
            if DeltaTime(str(product.update_time), item['update_time']) < UPDATE_DETAIL_TIEM_INTERVAL:
                item['is_update_product'] = False
                
            query = spider.session.query(ProductPriceObj)
            price = query.filter(ProductPriceObj.product_pkey == pkey).order_by(ProductPriceObj.update_time.desc()).first()
            if price:
                item['last_price'] = price.price
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
        else:
            return None   

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            #raise DropItem("Item contains no images")
            info.spider.log("%s : Item contains no images" % self.__class__, log.INFO)
            
        for image_path in image_paths:
            full_path = PRICE_IMAGES_STORE +'/'+image_path
            try:
                im = Image.open(full_path)
                #text = image_to_string(im)
                text = image_file_to_string(full_path)
                text = self._fixed_string(text)
                item['price'] = text[2:].strip()
            except:
                item['price'] = None
                raise
            
        self.test(item)
        return item

    def handle_error(self,e):
        log.err(e)
        
    def test(self, item):
        test = dict()
        item_keys = item.keys()
        if item['is_update_product']:       
            product_keys = ['is_update_product', 'pkey', 'price', 'last_price', 'url', 'image', 'origin_image_url', 'update_time', 'pstatus', 'product_id']
        else:
            product_keys = ['is_update_product', 'pkey', 'price', 'last_price', 'update_time']
        for ckey in product_keys:
                if ckey in item_keys:
                    test[ckey] = item[ckey]
        line = json.dumps(test)+"\n"
        self.file.write(line)
        
    '''
    The results of analysis that photographs
    '''
    def _fixed_string(self, string):
        string = string.lower()
        string = string.replace('o', '0')
        string = string.replace('s', '3')
        string = string.replace('z', '2')
        return string
        
"""
Download Product's image
"""       
class CyeProductImagesPipeline(ImagesPipeline):
    
    def __init__(self, store_uri, download_func=None):
        super(CyeProductImagesPipeline, self).__init__(store_uri, download_func=download_func)
        self.file = open('product_image.jl', 'wb')
    
    def get_media_requests(self, item, info):
        if item['is_update_product'] and item['origin_image_url'] is not None:
            image_url = item['origin_image_url']
            return [Request(image_url)]
        else:
            return None
        
    
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            #raise DropItem("Item contains no images")
            info.spider.log("%s : Item contains no images" % self.__class__, log.INFO)

        for image_path in image_paths:
            item['image'] = os.path.basename(image_path.strip())
            break
        return item
    
    def image_key(self, url):
        image_guid = hashlib.sha1(url).hexdigest()
        return 'images/full/%s.jpg' % (image_guid)

    def thumb_key(self, url, thumb_id):
        image_guid = hashlib.sha1(url).hexdigest()
        return 'images/thumbs/%s/%s.jpg' % (thumb_id, image_guid)

    def handle_error(self,e):
        log.err(e)
        
    def test(self, item):
        test = dict()
        item_keys = item.keys()
        if item['is_update_product']:       
            product_keys = ['is_update_product', 'pkey', 'price', 'last_price', 'url', 'image', 'origin_image_url', 'update_time', 'pstatus', 'product_id']
        else:
            product_keys = ['is_update_product', 'pkey', 'price', 'last_price', 'update_time']
        for ckey in product_keys:
                if ckey in item_keys:
                    test[ckey] = item[ckey]
        line = json.dumps(test)+"\n"
        self.file.write(line)


"""
Data writing database
"""
class CyeToDBPipeline(object):
    def __init__(self):
        self.product = None
        self.price = None
        self.file = open('price_change.jl', 'wb')
        self.last = open('last.jl', 'wb')
        
    def process_item(self, item, spider):
        self.doComplete(item, spider)
        return item 
    
    def _handle_detail(self, item, spider, product):
        if 'detail' in item.keys() and item['detail'] is not None:
            myfilter = getattr(CyeFilter, CyeFilter.getFilterClassName(spider.namespace))
            detail_dict = myfilter.handleDetail(item['detail'])
            myfilter.detail2Product(detail_dict, product)
            
    def _treate_product(self, item, spider):
        #item['is_update_product'] or 
        if True:
            self.product = item['product']
            if item['product_id'] is None or item['is_update_product']:
                self._item_to_product(item, self.product)
                self._handle_detail(item, spider, self.product)
    
    def _item_to_product(self, item, product):
        item_keys = item.keys()
        product_keys = ['pkey', 'title', 'url', 'image', 'origin_image_url', 'update_time', 'pstatus']
        for ckey in product_keys:
            if ckey in item_keys:
                setattr(product, ckey, item[ckey])
                
    def _treate_price(self, item, spider):
        isNew = False
        if item['last_price'] is None:
            isNew = True
        elif self.hasPriceChange(item['last_price'], item['price']):
            isNew = True
             
        if isNew:
            self.price = ProductPriceObj()
            self._handle_price(item, spider, self.price)
        else:
            self.price = None
            
    def _handle_price(self, item, spider, price):
        item_keys = item.keys()
        _keys = ['product_pkey', 'price', 'update_time']
        for ckey in _keys:
            if ckey in item_keys:
                setattr(price, ckey, item[ckey])
                    
    def doComplete(self, item, spider):
        self._treate_product(item, spider)
        self._treate_price(item, spider)
        
        self.test(item)
        
        if self.product:
            spider.session.add(self.product)
        if self.price:
            spider.session.add(self.price)
            self.testChange(item)
            
        #spider.session.flush()
    def hasPriceChange(self, one, two):
        if (two is not None) and cmp(one, two) == -1:
            return True
        else:
            return False
    
    def testChange(self, item):
        test={}
        test['pkey'] = item['pkey']
        test['is_update_product'] = item['is_update_product']
        test['last_price'] = item['last_price']
        test['price'] = item['price']
        
        line = json.dumps(test)+"\n"
        self.file.write(line)
        
    def test(self, item):
        test = dict()
        item_keys = item.keys()
        product_keys = ['is_update_product', 'pkey', 'price', 'last_price', 'url', 'image', 'origin_image_url', 'update_time', 'pstatus', 'product_id']
        for ckey in product_keys:
                if ckey in item_keys:
                    test[ckey] = item[ckey]
        line = json.dumps(test)+"\n"
        self.last.write(line)
