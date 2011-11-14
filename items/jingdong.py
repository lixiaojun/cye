# -*- coding: utf-8 -*-
'''
Created on 2011-11-9

@author: lixiaojun
'''
from scrapy.item import Item, Field

#Jd = jingdong
class JdCategoryItem(Item):
    
    url = Field()
    title = Field()
    status = Field()
    lastmodify_time = Field()
    ctype = Field()
    queue_key = Field()
    parent_key = Field()
    isdir = Field()
    
    pass