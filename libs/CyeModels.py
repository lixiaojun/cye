# -*- coding: utf-8 -*-
'''
Created on 2011-12-24

@author: qianmu.lxj
'''
from libs.CyeTools import CyeGiftDBpool, CyeDBpool
from twisted.enterprise import row
from twisted.enterprise.sqlreflector import SQLReflector


class ProductRow(row.RowObject):
    rowColumns = [("id", "int"),
                  ("pkey", "varchar"),
                  ("title", "varchar"),
                  ("url", "varchar"),
                  ("name", "varchar"),
                  ("add_time", "time"),
                  ("image", "varchar"),
                  ("origin_image_url", "varchar"),
                  ("producer", "varchar"),
                  ("production_place", "varchar"),
                  ("gross_weight", "varchar"),
                  ("status", "varchar"),
                  ("update_time", "time")]
    rowKeyColumns = [("id", "int4")]
    rowTableName = "product"
    
class ProductPriceRow(row.RowObject):
    rowColumns = [
                  ("id", "int"),
                  ("product_pkey", "varchar"),
                  ("price", "varchar"),
                  ("update_time", "time")
                  ]
    rowKeyColumns = [("id", "int4")]
    rowTableName = "product_price"
    
    

    
ProductReflector = SQLReflector(CyeGiftDBpool, [ProductRow])

PriceReflector = SQLReflector(CyeGiftDBpool, [ProductPriceRow])


