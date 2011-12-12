# -*- coding: utf-8 -*-
'''
Created on 2011-10-19

@author: lixiaojun
'''

from HTMLParser import HTMLParser
from items.jingdong import JdDataItem, JdProductItem, JdProductLoader
from libs.cyetools import CyeRedis
from scrapy import log
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector

from scrapy.conf import settings
settings.overrides['ITEM_PIPELINES'] = ['pipelines.jingdong.JsonWritePipeline']

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
              #安全套
            'http://www.360buy.com/products/1318-1467-1502.html',
             #手机
            'http://www.360buy.com/products/652-653-655.html',
             #笔记本
            'http://www.360buy.com/products/670-671-672.html',
            #平板电脑
            'http://www.360buy.com/products/670-671-2694.html'
         ]
        
        
        self.rules = [
            Rule(SgmlLinkExtractor(allow=['/\d+\.html']), 'parse_product')
         ]
        
        next_request_regx = self._getRuleRegular(self.start_urls)
        self.log("Category Regular expression : %s" % (next_request_regx), log.INFO)
        link_extr = SgmlLinkExtractor(allow=next_request_regx)
        next_rule = Rule(link_extr, 'parse_Request')
        self.rules.append(next_rule)
        
        #To initialize start_urls
        self.seed_key = self.namespace + ":" + self.name + ":" + "seeds"
        
        #get url list from redis
        self.redis_cli = CyeRedis.getInstance()
        
    
    def parse_product(self, rep):
        hx = HtmlXPathSelector(rep)
        
        loader = JdProductLoader(selector=hx)
        
        loader.add_value('product_url', rep.url)
        product_id = ((rep.url).split('/')[-1]).split('.')[0]
        loader.add_value('product_id', product_id)
        
        product_title = hx.select("//div[@id='name']/h1/text()").extract()
        if product_title is not None and len(product_title) > 0:
            product_title = product_title[0].strip()
            loader.add_value('product_title', self.strip_tags(product_title))
        
        loader.add_xpath('price_img_url', "//div[@class='fl']/strong[@class='price']/img/@src[1]")
        loader.add_xpath('product_img_url', "//div[@id='preview']//img/@src[1]")
        
        #loader.add_xpath('product_summary', "//ul[@id='summary']")
        
        #loader.add_xpath('product_detail', "//ul[@id='i-detail']")

        return loader.load_item()
    
    '''
    处理列页面，对其发送新的请求数据
    '''
    def parse_Request(self, rep):
        self.log('New Request: %s' % rep.url, log.INFO)
        return self.make_requests_from_url(rep.url)
         
        
    
    def _getRuleRegular(self, urls):
        allows = []
        reg_suffix = r"(-\d){9}(-\d{1,4})\.html"
        for x in urls:
            tmp = (x.split('/')[-1]).split('.')[0]
            if tmp is not None and len(tmp) > 0:
                tmp += reg_suffix
                allows.append(tmp)
        if len(allows) == 0:
            tmp = r'\d{3,6}-\d{3,6}-\d{3,6}' + reg_suffix
            allows.append(tmp)
            
        #append regular to catch links of category
        #allows.append('\d{3,6}-\d{3,6}-\d{3,6}\.html')
        
        return allows
    
    def strip_tags(self, html):
        html = html.strip()
        html = html.strip("\n")
        result = []
        parse = HTMLParser()
        parse.handle_data = result.append
        parse.feed(html)
        parse.close()
        return "".join(result)
    
    pass
