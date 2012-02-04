# -*- coding: utf-8 -*-
'''
Created on 2011-10-18

@author: lixiaojun
'''
# test by pipeline
from libs import CyeFilter
from libs.CyeModels import ProductReflector, ProductRow, ProductPriceRow, \
    PriceReflector
from libs.CyeTools import CyeGiftCursor
from libs.pytesser.pytesser import image_to_string, image_file_to_string
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
import string
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
        self.giftcursor = CyeGiftCursor
        
    def process_item(self, item, spider):
        self.setInfo(item)
        #line = json.dumps(dict(item))+"\n"
        #self.file.write(line)
        return item
    
    def setInfo(self, item):
        if 'pkey' in item.keys() and item['pkey'] is not None:
            self._setItemInfo(item)
            
    def _setItemInfo(self, item):
        pkey = item['pkey']
        item['product_pkey'] = item['pkey']
        product_sql = "SELECT * FROM `product` WHERE pkey='%s' LIMIT 1" % pkey
        product = self.giftcursor.execute(product_sql)
        if product:
            product = self.giftcursor.fetchone()
            item['product_id'] = product[0]
            if DeltaTime(str(product[-2]), item['update_time']) < UPDATE_DETAIL_TIEM_INTERVAL:
                item['is_update_product'] = False
            price_sql = "SELECT * FROM `product_price` WHERE product_pkey='%s' ORDER BY update_time DESC LIMIT 1" % pkey
            price = self.giftcursor.execute(price_sql)
            if price:
                price = self.giftcursor.fetchone()
                item['last_price'] = price[2]
            else:
                item['last_price'] = None
        
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
            im = Image.open(full_path)
            #text = image_to_string(im)
            text = image_file_to_string(full_path)
            text = self._fixed_string(text)
            item['price'] = text[2:].strip()
        line = json.dumps(dict(item))+"\n"
        self.file.write(line)
        return item

    def handle_error(self,e):
        log.err(e)
        
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
        print self.__class__
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



"""
Data writing database
"""
class CyeToDBPipeline(object):
    def __init__(self):
        self.prow = ProductRow()
        self.pricerow = ProductPriceRow()
        self.file = open('todb.jl', 'wb')
        
    def process_item(self, item, spider):
        self.doRow(item, spider)
        line = json.dumps(dict(self.prow.__dict__))+"\n"
        self.file.write(line)
        line = json.dumps(dict(self.pricerow.__dict__))+"\n"
        self.file.write(line)
        return item 
    
    def handle_detail(self, item, spider, row):
        if 'detail' in item.keys() and item['detail'] is not None:
            myfilter = getattr(CyeFilter, CyeFilter.getFilterClassName(spider.namespace))
            detail_dict = myfilter.handleDetail(item['detail'])
            myfilter.detail2Model(detail_dict, row)
            
    def handle_price(self, item, spider,pricerow):
        pricerow.assignKeyAttr('id', 0)
        self._priceItem2Row(item, pricerow)
        
    def _productItem2Row(self, item, row):
        if 'product_id' in item.keys() and item['product_id']:
            row.assignKeyAttr('id', item['product_id'])
        else:
            row.assignKeyAttr('id', 0)
        self.item2Row(item, row)
        
    def _priceItem2Row(self, item, row):
        self.item2Row(item, row)
        
    def item2Row(self, item, row):
        item_keys = item.keys()
        rowkey_attrs = [ attr for attr, t in row.rowKeyColumns ]
        for attr, value in  row.rowColumns:
            if attr in item_keys:
                if attr in rowkey_attrs:
                    row.assignKeyAttr(attr, item[attr])
                else:
                    setattr(row, attr, item[attr])
                    
    def doRow(self, item, spider):
        
        def _callback_info(datas):
            pass
        
        if item['is_update_product']:
            self._productItem2Row(item, self.prow)
            self.handle_detail(item, spider, self.prow)
            #CyeFilter.row2Unicode(self.prow)
            
            if self.prow.id == 0:
                ProductReflector.insertRow(self.prow).addCallback(_callback_info)
            else:
                ProductReflector.updateRow(self.prow).addCallback(_callback_info)
            
        if not ('last_price' in item.keys()):
            item['last_price'] = "0.00"
        if 'price' in item.keys() \
            and self._isPriceChange(item['price'], item['last_price']):
            self.handle_price(item, spider, self.pricerow)
            PriceReflector.insertRow(self.pricerow).addCallback(_callback_info)
        
    
    """
    Compare two strings about price
    """
    def _isPriceChange(self, one, two):
        if not (one or two):
            return False
        if one is not two:
            return True
        return False
            
