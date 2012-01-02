# -*- coding: utf-8 -*-
'''
Created on 2011-10-19

@author: lixiaojun
'''

from cyespider.items import CyeProductLoader
from libs.cyetools import CyeRedis
from scrapy import log
from scrapy.conf import settings
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
import hashlib
import re

settings.overrides['ITEM_PIPELINES'] = ['pipelines.jingdong.JsonWritePipeline',
                                        'pipelines.jingdong.CyePriceImagesPipeline',
                                        #'pipelines.jingdong.CyeProductImagesPipeline'
                                        ]

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
            #TT/cellphone/notebook PC/tablet PC
            'http://www.360buy.com/products/1318-1467-1502.html',
            #'http://www.360buy.com/products/652-653-655.html',
            #'http://www.360buy.com/products/670-671-672.html',
            #'http://www.360buy.com/products/670-671-2694.html'
         ]
        
        
        self.rules = [
            Rule(SgmlLinkExtractor(allow=['/\d+\.html']), 'parse_product')
         ]
        self.rules.append(self._getNextRuleByUrl(self.start_urls, 'parse_Request'))
        
        #To initialize start_urls
        self.seed_key = self.namespace + ":" + self.name + ":" + "seeds"
        
        #redis instance
        self.redis_cli = CyeRedis.getInstance()
        
    
    def parse_product(self, rep):
        hx = HtmlXPathSelector(rep)
        
        ploader = CyeProductLoader(selector=hx)
        
        ploader.add_value('url', rep.url)
        ploader.add_value('pkey', hashlib.md5(rep.url).hexdigest())
        
        product_title = hx.select("//div[@id='name']/h1/text()").extract()
        if product_title is not None and len(product_title) > 0:
            product_title = product_title[0].strip()
            ploader.add_value('title', self.strip_tags(product_title))
        
        ploader.add_xpath('price_image_url', "//strong[@class='price']/img/@src")
        ploader.add_xpath('origin_image_url', "//div[@id='preview']//img/@src")
        
        #ploader.add_xpath('detail', "//ul[@id='i-detail']")
        
        return ploader.load_item()
    
    '''
    Handle new Request
    '''
    def parse_Request(self, rep):
        self.log('New Request: %s' % rep.url, log.INFO)
        return self.make_requests_from_url(rep.url)
    
         
    def parse_nothing(self, rep):
        raise Exception('Not designated analytic functions. url[%s]' % rep.url)
        
    '''
    Get Rule by start urls.
        @param urls: The start urls of scrapy
        @param func_name: Use to parse response
    '''
    def _getNextRuleByUrl(self, urls, func_name='parse_nothing'):
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
        self.log("Category Regular expression : %s" % (allows), log.INFO)
        link_extr = SgmlLinkExtractor(allow=allows)
        next_rule = Rule(link_extr, func_name)
        return next_rule
        
    
    def strip_tags(self, html):
        html = html.strip()
        html = html.strip("\n")
        p = re.compile(r'<.*?>')
        return p.sub('', html)
        
    
    pass
