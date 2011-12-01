# -*- coding: utf-8 -*-
'''
Created on 2011-10-19

@author: lixiaojun
'''

from items.jingdong import JdDataItem, JdProductItem, JdProductLoader
from libs.cyetools import CyeRedis
from scrapy import log
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector


class JingdongSpider(CrawlSpider):
    name = 'jingdong_crawl'
    namespace = "jingdong"
    allowd_domains = ['360buy.com']
    baseUrl = "http://www.360buy.com/products/"
    
    def __init__(self, *a, **kw):
        self.initCye()
        super(JingdongSpider, self).__init__(*a, **kw)

        
    def initCye(self):
        
        self.start_urls = [
            'http://www.360buy.com/products/1318-1467-1502.html'
         ]
        
        
        self.rules = [
            Rule(SgmlLinkExtractor(allow=['/\d+\.html']), 'parse_product')
         ]
        next_request_regx = self._getRuleRegular(self.start_urls)
        self.log("Category Regular expression : %s" % (next_request_regx), log.INFO)
        link_extr = SgmlLinkExtractor(allow=next_request_regx)
        next_rule = Rule(link_extr, 'parse_other')
        #self.rules.append(next_rule)
        
        #To initialize start_urls
        self.seed_key = self.namespace+":"+self.name+":"+"seeds"
        
        #get url list from redis
        self.redis_cli = CyeRedis.getInstance()
        
    
    def parse_product(self, rep):
        hx = HtmlXPathSelector(rep)
        
        loader = JdProductLoader(selector=hx)
        
        loader.add_value('product_url', rep.url)
        product_id = ((rep.url).split('/')[-1]).split('.')[0]
        loader.add_value('product_id', product_id)
        
        loader.add_xpath('product_title', "//div[@id='name']/h1/text()")
        loader.add_xpath('price_img_url', "//div[@class='fl']/strong[@class='price']/img/@src[1]")
        loader.add_xpath('product_img_url', "//div[@id='preview']//img/@src[1]")
        
        return loader.load_item()
    
    def parse_other(self, rep):
        self.log('Next Page: %s' % rep.url)
        #return self.make_requests_from_url(rep.url)
        #return Request(rep.url, self.parse_nextpage)
        
    
    def _getRuleRegular(self, urls):
        allows = []
        reg_suffix = r"[-\d]*?\.html"
        for x in urls:
            tmp = (x.split('/')[-1]).split('.')[0]
            if tmp is not None and len(tmp) > 0:
                tmp += reg_suffix
                allows.append(tmp)
        if len(allows) == 0:
            tmp = r'\d{3,6}-\d{3,6}-\d{3,6}(-\d{3,6})?' + reg_suffix
            allows.append(tmp)
        return allows
    
    pass
