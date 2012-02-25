'''
Created on 2012-2-16

@author: lixiaojun
'''
from cyespider.items import CyeProductLoader
from cyespider.spiders.JingdongSpider import JingdongSpider
from libs.CyeTools import MygiftSession, CyeRedis, ProductObj, ProductPriceObj
from scrapy import log
from scrapy.conf import settings
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from sqlalchemy.orm import scoped_session
from sqlalchemy.sql.expression import or_
import hashlib
import re
import time
#from fooSpider.pipelines import FooPipeline
#settings.overrides['ITEM_PIPELINES'] = ['fooSpider.pipelines.FooImagePipeline']

crawl_time_interval = settings.get('UPDATE_CRAWL_TIME_INTERVAL', 6)
lite_max_num = settings.get('UPDATE_CRAWL_TIME_INTERVAL', 15)
update_max_num = settings.get('UPDATE_CRAWL_MAX_NUM', 1500)

class JingdongUpdateSpider(BaseSpider):
    name = "jingdong_update"
    namespace = "jingdong"
    base_url = "http://www.360buy.com/"
    start_urls = [
                    #"http://www.360buy.com/product/358209.html", 
                    #"http://www.360buy.com/product/507269.html", 
                    #"http://www.360buy.com/product/341970.html",
                  ]
    
    def __init__(self, **kw):
        self._init_urls()
        super(JingdongUpdateSpider, self).__init__(self.name, **kw)
        
    def _init_urls(self):
        self.session = scoped_session(MygiftSession)
        self.query_product = self.session.query(ProductObj)
        self.query_price = self.session.query(ProductPriceObj)
        
        query = self.session.query(ProductObj.url)
        myquery = query.filter(or_("last_crawl_time is null", "last_crawl_time<DATE_ADD(NOW(), INTERVAL :time_interval HOUR)")).\
            params(time_interval=crawl_time_interval)
        if update_max_num > 0:
            myquery = myquery.limit(update_max_num)
        results = myquery.all()
        for url, in results:
            self.start_urls.append(url)
        self.log('Update the number of links : %d' % len(results), log.INFO)

    def parse(self, response):
        if self.isJingdongProduct(response.url):
            return self.parse_product(response)
        
    def parse_product(self, rep):
        return JingdongSpider.responseToItem(rep)

    def strip_tags(self, html):
        html = html.strip()
        html = html.strip("\n")
        p = re.compile(r'<.*?>')
        return p.sub('', html)
    
    def isJingdongProduct(self, url):
        flag = False
        regExp = "360buy\.com/product/\d+\.(html)"
        match = re.search(regExp, url)
        if match:
            flag = True
        return flag
    

class JingdongUpdateLiteSpider(BaseSpider):
    name = "jingdong_update_lite"
    namespace = "jingdong"
    base_url = "http://www.360buy.com/"
    start_urls = []
    
    def __init__(self, **kw):
        self._init_urls()
        super(JingdongUpdateLiteSpider, self).__init__(self.name, **kw)
        
    def _init_urls(self):
        self.session = scoped_session(MygiftSession)
        self.query_product = self.session.query(ProductObj)
        self.query_price = self.session.query(ProductPriceObj)
        
        self.redis_cli = CyeRedis.getInstance()
        self.session = scoped_session(MygiftSession)
        self.update_urls_key = settings.get('REDIS_UPDATE_URLS_KEY', '%s:update') % self.namespace
        results = self.redis_cli.zrange(self.update_urls_key, 0, lite_max_num, withscores=True)
        
        if results:
            self.start_urls.extend(results)
            self.log("The number of  links : %d" % len(results), log.INFO)
        else:
            self.log("Not found link to update.", log.INFO)
        

    def parse(self, response):
        if self.isJingdongProduct(response.url):
            return self.parse_product(response)
        
    def parse_product(self, rep):
        return JingdongSpider.responseToItem(rep)

    def strip_tags(self, html):
        html = html.strip()
        html = html.strip("\n")
        p = re.compile(r'<.*?>')
        return p.sub('', html)
    
    def isJingdongProduct(self, url):
        flag = False
        regExp = "360buy\.com/product/\d+\.(html)"
        match = re.search(regExp, url)
        if match:
            flag = True
        return flag