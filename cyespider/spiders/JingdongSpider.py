# -*- coding: utf-8 -*-
'''
Created on 2011-10-19

@author: lixiaojun
'''

from items.jingdong import JdDataItem
from libs.cyetools import CyeRedis
from lxml.builder import partial
from scrapy.conf import settings
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
import sys
#from libs.cyesgml import SgmlLinkExtractor


class JingdongSpider(CrawlSpider):
    name = 'jingdong_crawl'
    _namespace = "jingdong"
    allowd_domains = ['360buy.com']
    baseUrl = "http://www.360buy.com/products/"
    
    def __init__(self, *a, **kw):
        super(JingdongSpider, self).__init__(*a, **kw)
        self.initCye()
        
    def initCye(self):
        print sys.argv
        
        start_urls = [
            'http://www.360buy.com/products/1318-1467-1502.html'
         ]
        new_res_regx = self._getPRegxFormUrls(start_urls)
        rules = [
            Rule(SgmlLinkExtractor(allow=['/\d+\.html']), 'parse_product'),
            Rule(SgmlLinkExtractor(allow=[new_res_regx]), 'parse_other')
         ]
        
        #To initialize start_urls
        self._cyecfg['seed_list_key'] = self._namespace+":"+self.name+":"+"seeds"
        
        #get url list from redis
        self.redis_cli = CyeRedis.getInstance()
        
    
    def parse_product(self, rep):
        hx = HtmlXPathSelector(rep)
        jd = JdDataItem()
        
        jd['url'] = rep.url
        jd['title'] = hx.select("//div[@id='name']/h1/text()").extract()
        
        #self.log("Name:"+jd['name'], "DEBUG")
        return jd
    
    def parse_other(self, rep):
        self.log('Next Page: %s' % rep.url)
        #return self.make_requests_from_url(rep.url)
        #return Request(rep.url, self.parse_nextpage)
        
    
    def _getPRegxFormUrls(self, urls):
        regx = ""
        for x in urls:
            tmp = (x.split('/')[-1]).split('.')[0]
            if tmp is not None:
                tmp = '('+tmp+')'
                regx += '|'
        if len(regx) > 0:
            regx = regx[:-1]
        else:
            regx = "\d{3,6}-\d{3,6}-\d{3,6}(-\d{3,6})?"
        regx = regx+".?*\.html"
        return regx
    
    pass
