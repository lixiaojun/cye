# -*- coding: utf-8 -*-
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


#SCHEDULER = 'cyecore.scheduler.Scheduler'
#SCHEDULER_PERSIST = True

IMAGES_STORE = '/home/admin/static'
IMAGES_THUMBS = {
                 'small': (50, 50),
                 'big': (270, 270),
                 }

MYSQLDB_CONF = {
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'passwd': 'wishlist2012'
                }

REDISDB_CONF = {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'passwd': 'hello1234'
              }

REDIS_UPDATE_URLS_KEY="%s:update"

UPDATE_CRAWL_TIME_INTERVAL=8    #hour Update time interval
UPDATE_CRAWL_MAX_NUM=3000        #Each update the largest number
UPDATE_LITE_CRAWL_MAX_NUM = 15   #Every time grab the largest number
UPDATE_DETAIL_TIEM_INTERVAL = 7  #Updated detail time interval

START_URLS ={
             'jingdong':[
                    #TT/cellphone/notebook PC/tablet PC
                    #'http://www.360buy.com/products/1318-1467-1502.html',          #避孕套
                    'http://www.360buy.com/products/652-653-655.html',              #手机
                    'http://www.360buy.com/products/670-671-672.html',              #笔记本电脑
                    'http://www.360buy.com/products/670-671-2694.html',             #平板电脑
                    'http://www.360buy.com/products/670-671-673.html',              #台式机
                    'http://www.360buy.com/products/652-654-831.html',              #数码相机
                    'http://www.360buy.com/products/652-654-832.html',              #单反相机
                    'http://www.360buy.com/products/652-654-834.html',              #单反镜头
                    'http://www.360buy.com/products/737-794-798.html',              #平板电视
                    'http://www.360buy.com/products/737-794-1199.html',             #迷你音箱
                    
                ],
             }
