# Scrapy settings for cyespider project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'cyespider'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['cyespider.spiders']
NEWSPIDER_MODULE = 'cyespider.spiders'
DEFAULT_ITEM_CLASS = 'cyespider.items.CyespiderItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)


SCHEDULER = 'cyecore.scheduler.Scheduler'
SCHEDULER_PERSIST = False

IMAGES_STORE = '/home/lixiaojun/scrapy'
IMAGES_THUMBS = {
                 'small': (50, 50),
                 'big': (270, 270),
                 }

MYSQLDB_CONF = {
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'passwd': '123456'
                }

REDISDB_CONF = {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'passwd': 'hello1234'
              }

'''
Updated detail time interval
'''
UPDATE_DETAIL_TIEM_INTERVAL = 0
