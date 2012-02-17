# -*- coding: utf-8 -*-
'''
Created on 2011-10-19

@author: lixiaojun
'''

from cyespider.items import CyeProductLoader
from libs.CyeTools import CyeRedis, MygiftSession
from scrapy import log
from scrapy.conf import settings
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from sqlalchemy.orm import scoped_session
import hashlib
import re
import time


settings.overrides['ITEM_PIPELINES'] = [
                                        'cyespider.pipelines.SessionPipeline',
                                        'cyespider.pipelines.CyeFirstPipeline',
                                        'cyespider.pipelines.CyePriceImagesPipeline',
                                        'cyespider.pipelines.CyeProductImagesPipeline',
                                        'cyespider.pipelines.CyeToDBPipeline'
                                            ]

class JingdongSpider(CrawlSpider):
    name = 'jingdong_crawl'
    namespace = "jingdong"
    allowd_domains = ['360buy.com']
    baseUrl = "http://www.360buy.com/products/"
    
    session = None
    
    def __init__(self, *a, **kw):
        self.initCye()
        super(JingdongSpider, self).__init__(*a, **kw)

        
    def initCye(self):
        
        self.start_urls = [
            #TT/cellphone/notebook PC/tablet PC
            #'http://www.360buy.com/products/1318-1467-1502.html',
            'http://www.360buy.com/products/652-653-655.html',              #手机
            'http://www.360buy.com/products/670-671-672.html',              #笔记本电脑
            'http://www.360buy.com/products/670-671-2694.html',             #平板电脑
            'http://www.360buy.com/products/670-671-673.html',              #台式机
            'http://www.360buy.com/products/652-654-831.html',              #数码相机
            'http://www.360buy.com/products/652-654-832.html',              #单反相机
            'http://www.360buy.com/products/652-654-834.html',              #单反镜头
         ]
        
        
        self.rules = [
            Rule(SgmlLinkExtractor(allow=['/\d+\.html']), 'parse_product')
         ]
        self.rules.append(self._getNextRuleByUrl(self.start_urls, 'parse_Request'))
        
        self.session = scoped_session(MygiftSession)
        
        #self.urls_key = settings.get('REDIS_URLS_KEY', '%s:urls') % self.namespace
        
        #redis instance
        self.redis_cli = CyeRedis.getInstance()
        
    
    def parse_product(self, rep):
        hx = HtmlXPathSelector(rep)
        
        ploader = CyeProductLoader(selector=hx)
        
        ploader.add_value('url', rep.url)
        ploader.add_value('pkey', hashlib.md5(rep.url).hexdigest())
        ploader.context['item']['is_update_product'] = True
        ploader.add_value('update_time', time.strftime('%Y-%m-%d %X', time.localtime()))
        ploader.add_value('pstatus', 'on')
        
        product_title = hx.select("//div[@id='name']/h1/text()").extract()
        if product_title is not None and len(product_title) > 0:
            product_title = product_title[0].strip().encode('utf-8')
            ploader.add_value('title', self.strip_tags(product_title))
        
        ploader.add_xpath('price_image_url', "//strong[@class='price']/img/@src")
        ploader.add_xpath('origin_image_url', "//div[@id='preview']//img/@src")
        
        
        ploader.add_xpath('detail', "//ul[@id='i-detail']")
        
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
