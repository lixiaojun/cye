# -*- coding: utf-8 -*-
'''
Created on 2011-11-9

@author: lixiaojun

Modified on 2011-11-18

@author: Geph0rce
'''
from scrapy.item import Item, Field
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import MapCompose, TakeFirst, Join

#Jd = jingdong
class JdProductItem(Item):
    
    product_id = Field()
    product_url = Field()
    product_price = Field()
    product_title = Field()
    price_img_url = Field()
    product_img_url = Field()
    product_img_path = Field()
    product_summary = Field()
    product_specifications = Field()
    product_detail = Field()
    
    pass
   
class JdProductLoader(XPathItemLoader):
    default_item_class = JdProductItem
    default_input_processor = MapCompose(lambda s: s.strip())
    default_output_processor = TakeFirst()
    description_out = Join()

class JdDataItem(Item):
    url = Field()
    title = Field()
    
    pass