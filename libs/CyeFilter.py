# -*- coding: utf-8 -*-
'''
Created on 2011-12-25

@author: qianmu.lxj
'''
from libs.BeautifulSoup import BeautifulSoup

FILTER_FORMAT = "%sFilter"
PAGE_CHARACTER = 'utf8'

class JingdongFilter(object):
    soup = None
    ITEM_NAME_KV_DETAIL = {'商品名称':'name', '生产厂家':'producer', '商品产地':'production_place', '商品毛重':'gross_weight', '上架时间':'add_time'}
    ITEM_SEPARATOR_DETAIL = "：".decode(PAGE_CHARACTER)
    
    @classmethod
    def handleDetail(cls, html):
        detail = {}
        cls.soup = BeautifulSoup(html)
        liTags = cls.soup.findAll('li')
        for tag in liTags:
            text = ''.join(tag.findAll(text=True))
            #print text.split(cls.ITEM_SEPARATOR_DETAIL)[1]
            item = text.split(cls.ITEM_SEPARATOR_DETAIL)
            key = item[0].encode(PAGE_CHARACTER)
            if key in cls.ITEM_NAME_KV_DETAIL.keys():
                dbkey = cls.ITEM_NAME_KV_DETAIL[key]
                detail[dbkey] = item[1].encode(PAGE_CHARACTER)  
        return detail
    """
    
    """
    @classmethod
    def detail2Model(cls, detail, row):
        if row is None:
            raise CyeFilterException("Model objects not initialized。")
        rowkey_attrs = [ attr for attr, t in row.rowKeyColumns ]
        for key in detail.keys():
            if key in rowkey_attrs:
                row.assignKeyAttr(key, detail[key])
            else:
                setattr(row, key, detail[key])

def GetFilter(prefix):
    pass

def getFilterClassName(prefix):
    if prefix is not None:
            prefix = (prefix.lower()).capitalize()
            
    return FILTER_FORMAT % prefix

def row2Unicode(row):
    rowkey_attrs = [ attr for attr, t in row.rowKeyColumns ]
    for key in rowkey_attrs:
        if isinstance(row.__dict__[key], str):
            row.__dict__[key] = row.__dict__[key].encode('utf8')
        

class CyeFilterException(Exception):
    """"""

    