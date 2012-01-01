# -*- coding: utf-8 -*-
'''
Created on 2011-12-25

@author: qianmu.lxj
'''
from libs.BeautifulSoup import BeautifulSoup

class JingdongFilter(object):
    soup = None
    ITEM_NAME_KV_DETAIL = {'商品名称':'name', '生产厂家':'producer', '商品产地':'production_place', '商品毛重':'gross_weight', '上架时间':'add_time'}
    ITEM_SEPARATOR_DETAIL = '：'
    
    @classmethod
    def handleDetail(cls, html):
        detail = {}
        
        cls.soup = BeautifulSoup(html)
        liTags = cls.soup.findAll('li')
        for tag in liTags:
            text = ''.join(tag.findAll(text=True))
            #print text.split(cls.ITEM_SEPARATOR_DETAIL)[1]
            item = text.split(cls.ITEM_SEPARATOR_DETAIL)
            key = item[0].encode('utf8')
            if key in cls.ITEM_NAME_KV_DETAIL.keys():
                dbkey = cls.ITEM_NAME_KV_DETAIL[key]
                detail[dbkey] = item[1].encode('utf8')
            
            
        return detail
    

    pass
    