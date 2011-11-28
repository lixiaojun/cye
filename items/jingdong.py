# -*- coding: utf-8 -*-
'''
Created on 2011-11-9

@author: lixiaojun

Modified on 2011-11-18

@author: Geph0rce
'''
from scrapy.item import Item, Field

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


class JdDataItem(Item):
    url = Field()
    title = Field()
    
    pass