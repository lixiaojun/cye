# -*- coding: utf-8 -*-
'''
Created on 2011-11-19

@author: lixiaojun
'''
from items.jingdong import JdCategoryItem
from libs.cyetools import CyeRedis
from libs.parsecfg import CyeCfg
from lxml.builder import partial
from scrapy.conf import settings
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
import hashlib
import sys

settings.overrides['ITEM_PIPELINES'] = []

class JdCrawlSpider(CrawlSpider):
    
    name = "jingdong_crawl_old"
    allowd_domains = ['360buy.com']
    baseUrl = "http://www.360buy.com/products/"
    
    def __init__(self, *a, **kw):
        super(JdCrawlSpider, self).__init__(*a, **kw)
        self.initCye()
    
    '''
    initialize conf of spider
    '''
    def initCye(self):
        print sys.argv
        
        argv = sys.argv
        pcfg = CyeCfg()
        if len(argv) < 3:
            raise Exception('JdCrawlSpider', "Missing argument. Please add spider option.")
        self._cyecfg = pcfg.getCfgFromJson(argv[2])
        self._check_cfg(self._cyecfg)
        
        self.start_urls = []
        self.start_urls.append(self._cyecfg['url'])
        self.rules = [
                      Rule(SgmlLinkExtractor(allow=['/\d+\.html']), 'parse_product'),
                      Rule(SgmlLinkExtractor(allow=['\d{3,6}-\d{3,6}-\d{3,6}-\d{3,6}(-\d){9}\.html']), 'parse_other')
                        ]
        
        #get url list from redis
        self.redis_cli = CyeRedis.getInstance()
        self.update_url_list = self.redis_cli.get(self._cyecfg['queue_key'])
        
        pass
    
    def parse_product(self, rep):
        hx = HtmlXPathSelector(rep)
        jd = JdCategoryItem()
        
        jd['url'] = rep.url
        jd['name'] = hx.select("//div[@id='name']/h1/text()").extract()
        jd['price'] = hx.select("//div[@class='fl']/strong[@class='price']").extract()
        jd['image'] = hx.select("//div[@id='spec-n1']").extract()
        #self.log("Name:"+jd['name'], "DEBUG")
        return jd
    
    def parse_other(self, rep):
        self.log('Next Page: %s' % rep.url)
        #return self.make_requests_from_url(rep.url)
        #return Request(rep.url, self.parse_nextpage)
        
    #override
    def _requests_to_follow(self, response):
        seen = set()
        for rule in self._rules:
            links = [l for l in rule.link_extractor.extract_links(response) if l not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            seen = seen.union(links)
            #to update redis' url list
            self._update_url_list(links)
            
            for link in links:
                callback = partial(self._response_downloaded, callback=rule.callback, \
                    cb_kwargs=rule.cb_kwargs, follow=rule.follow)
                r = Request(url=link.url, callback=callback)
                r.meta['link_text'] = link.text
                yield rule.process_request(r)
        pass
    
    def _update_url_list(self, links):
        if links is not None:
            sets_links = set(links)
            tmp = self.update_url_list.union(links)
            rm_links = tmp - sets_links
            add_links = tmp - links
            for x in rm_links:
                if x is not None:
                    self.redis_cli.srem(self._cyecfg['queue_key'], x)
            for x in add_links:
                if x is not None:
                    self.redis_cli.sadd(self._cyecfg['queue_key'], x)
        pass
    
    def _check_cfg(self, cfg):
        if cfg is None or len(cfg) <= 0:
            raise Exception('JdCrawlSpider', 'Missing option.Now, option number:'+len(cfg))
        for (k, v) in cfg:
            if v is None:
                raise Exception('JdCrawlSpider', 'Init option[ '+k+' ] error.')
        pass
    pass
