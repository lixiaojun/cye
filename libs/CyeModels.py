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
                  ("add_time", "datetime"),
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
                  ("product_id", "int"),
                  ("price", "varchar"),
                  ("update_time", "time")
                  ]
    rowKeycolumns = [("id", "int4")]
    rowTableName = "product_price"
    
class CyeTbRow(row.RowObject):
    rowColumns = [("id", "int"),
                  ("pkey", "varchar"),
                  ("url", "varchar"),
                  ("title", "varchar"),
                  ("product_img_url", "varchar"),
                  ("product_img", "varchar"),
                  ("detail", "varchar"),
                  ("utime", "time")]
    rowKeyColumns = [("id", "int4"), ("pkey", "varchar")]
    rowTableName = "cye_tb"
    
    

    
ProductReflector = SQLReflector(CyeGiftDBpool, [ProductRow])

CyeTbReflector = SQLReflector(CyeDBpool, [CyeTbRow])

