# -*- coding: utf-8 -*-
'''
Created on 2011-10-19

@author: lixiaojun
'''

from cyespider.items import CyeProductLoader
from libs.CyeTools import CyeRedis, MygiftSession, ProductObj, ProductPriceObj
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

STATUS_PRODUCT_ONLINE = 'on'
STATUS_PRODUCT_NO_PRICE = 'wait'
    
class JingdongSpider(CrawlSpider):
    name = 'jingdong_crawl'
    namespace = "jingdong"
    allowd_domains = ['360buy.com']
    baseUrl = "http://www.360buy.com/products/"
    
    session = None
    _category_seen = []
    _without_region_regexp = r'(\d{3,6}-\d{3,6}-\d{3,6}(-\d){10})'
    
    def __init__(self, *a, **kw):
        self.initCye()
        super(JingdongSpider, self).__init__(*a, **kw)

        
    def initCye(self):
        self.session = scoped_session(MygiftSession)
        self.query_product = self.session.query(ProductObj)
        self.query_price = self.session.query(ProductPriceObj)
        
        self.start_urls = (settings.get('START_URLS'))[self.namespace]     
        self.rules = [
            Rule(SgmlLinkExtractor(allow=['/\d+\.html']), 'parse_product', process_links=self._process_product_links)
         ]
        self.rules.append(self._getNextRuleByUrl(self.start_urls, 'parse_Request'))
        
        #self.urls_key = settings.get('REDIS_URLS_KEY', '%s:urls') % self.namespace
        
        #redis instance
        self.redis_cli = CyeRedis.getInstance()
        
        
    def _process_product_links(self, links):
        new_links = []
        for link in links:
            pkey = hashlib.md5(link.url).hexdigest()
            query = self.query_product
            product = query.filter(ProductObj.pkey == pkey).first()
            if product is None:
                new_links.append(link)
            else:
                self.log('Skiped : %s' % link.url, log.INFO)
        return new_links
    
    def _process_category_links(self, links):  
        new_links = []
        for l in links:
            match = re.search(self._without_region_regexp, l.url)
            if match and match.group(0) not in self._category_seen:
                self._category_seen.append(match.group(0))
                new_links.append(l)            
        self.log('Category count : %d' % len(self._category_seen), log.INFO)
        return new_links
    
    def parse_product(self, rep):
        pkey = hashlib.md5(rep.url).hexdigest()
        query = self.session.query(ProductObj)
        product = query.filter(ProductObj.pkey == pkey).first()
        if product is None:
            return JingdongSpider.responseToItem(rep)
    
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
        reg_suffix = [r"(-\d){10}(-\d+)*\.html",]
        for x in urls:
            tmp = (x.split('/')[-1]).split('.')[0]
            if tmp is not None and len(tmp) > 0:
                for it in reg_suffix:
                    tmp += it
                    allows.append(tmp)
        if len(allows) == 0:
            tmp = r'\d{3,6}-\d{3,6}-\d{3,6}' + reg_suffix
            allows.append(tmp)
            
        #append regular to catch links of category
        #allows.append('\d{3,6}-\d{3,6}-\d{3,6}\.html')
        self.log("Category Regular expression : %s" % (allows), log.INFO)
        link_extr = SgmlLinkExtractor(allow=allows)
        next_rule = Rule(link_extr, func_name, process_links=self._process_category_links)
        return next_rule
        
    @classmethod
    def strip_tags(cls, html):
        html = html.strip()
        html = html.strip("\n")
        p = re.compile(r'<.*?>')
        return p.sub('', html)
    
    @classmethod
    def responseToItem(cls, rep):
        hx = HtmlXPathSelector(rep)
        
        ploader = CyeProductLoader(selector=hx)
        
        ploader.add_value('url', rep.url)
        ploader.add_value('pkey', hashlib.md5(rep.url).hexdigest())
        ploader.context['item']['is_update_product'] = True
        ploader.add_value('update_time', time.strftime('%Y-%m-%d %X', time.localtime()))
        
        product_title = hx.select("//div[@id='name']/h1/text()").extract()
        if product_title is not None and len(product_title) > 0:
            product_title = product_title[0].strip().encode('utf-8')
            ploader.add_value('title', cls.strip_tags(product_title))
            
        price_url_regexp = r"price.360buyimg.com/gp\d+"
        price_image_url = hx.select("//strong[@class='price']/img/@src").extract()
        if len(price_image_url)>0 and re.search(price_url_regexp, price_image_url[0]):
            ploader.add_value('pstatus', STATUS_PRODUCT_ONLINE)
            ploader.add_value('price_image_url', price_image_url)
        else:
            ploader.add_value('pstatus', STATUS_PRODUCT_NO_PRICE)
            ploader.add_value('price_image_url', None)
        ploader.add_xpath('origin_image_url', "//div[@id='preview']//img/@src")
        
        ploader.add_xpath('detail', "//ul[@id='i-detail']")
        
        return ploader.load_item()
    
    pass
