'''
Created on 2011-12-24

@author: qianmu.lxj
'''
from scrapy.conf import settings
from twisted.enterprise import row, adbapi
from twisted.enterprise.sqlreflector import SQLReflector

'''
Connect database
'''
dbconf = settings.get('MYSQLDB_CONF')

DB_PORT   = dbconf.get('port', 3306)
DB_USER   = dbconf.get('user', 'root')
DB_HOST   = dbconf.get('host', 'localhost')
DB_PASSWD = dbconf.get('passwd', '123456')

cyeDBpool = adbapi.ConnectionPool('MySQLdb', host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWD, \
                                  db='cye_db',use_unicode=True, charset='utf8')
giftDBpool = adbapi.ConnectionPool("MySQLdb", host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWD, \
                                   db='mygift',use_unicode=True, charset='utf8')



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
                  ("utime", "datetime")]
    rowKeyColumns = [("pkey", "varchar"), ("id", "int4")]
    rowTableName = "product"
    
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
    
    

    
ProductReflector = SQLReflector(giftDBpool, [ProductRow])

CyeTbReflector = SQLReflector(cyeDBpool, [CyeTbRow])

