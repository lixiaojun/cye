# -*- coding: utf-8 -*-
'''
Created on 2011-11-9

@author: lixiaojun
'''
from items.jingdong import JdCategoryItem
from scrapy.conf import settings
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.utils.url import urljoin_rfc
import hashlib
import sys

_is_valid_url = lambda url: url.split('://', 1)[0] in set(['http', 'https', 'file'])

#set pipeline
#settings.overrides['ITEM_PIPELINES'] = ["pipelines.jingdong.JsonWritePipeline"]

#Jd = jingdong
class JdCategorySpider(BaseSpider):
    
    name = 'jingdong_category'
    allowed_domains = ['www.360buy.com']
    baseUrl = "http://www.360buy.com"
    start_urls = ['http://www.360buy.com/allSort.aspx']
    
    def __init__(self, *a, **kw):
        super(JdCategorySpider, self).__init__(*a, **kw)
        self.initCye()
    
    '''
    initialize conf of spider
    '''
    def initCye(self):
        print settings.get("SCHEDULER")
        pass
    
    def parse(self, response):
        
        #通过html文本生成实体的列表
        category_items = self.__getItemsByXpth(response)
        return category_items
    
    def __getItemsByXpth(self, response):
        
        xp = HtmlXPathSelector(response)
        category_items = []
        
        category_one_items = []
        category_two_items = []
        category_thrd_items = []
        
        m_xpstr = "//div[@class='m']"
        for node in xp.select(m_xpstr):
            if node is not None:
                mt_a_node = node.select("div[@class='mt']//a")
                if mt_a_node is not None:
                    itemt = JdCategoryItem()
                    itemt['title'] = mt_a_node.select("text()").extract()[0]
                    print "[ %s ]" % (itemt['title'])
                    itemt['url'] = self.__getCompleteUrl(mt_a_node.select("@href").extract()[0])
                    key = itemt['title']+itemt['url']
                    itemt['queue_key'] = hashlib.md5(key.encode('utf8')).hexdigest().upper()
                    itemt['isdir'] = 'yes'
                    category_one_items.append(itemt)
                
                mc_node = node.select("div[@class='mc']")
                if mc_node is not None:
                        
                    for mc_dt_node in mc_node.select("dl/dt"):
                        if mc_dt_node is not None:
                            itemt_2 = JdCategoryItem()
                            if len(category_one_items) > 1:
                                text = mc_dt_node.select("a/text()").extract()
                                url = mc_dt_node.select("a/@href").extract()
                            else:
                                text = mc_dt_node.select("text()").extract()
                                url = mc_dt_node.select("@href").extract()
                            itemt_2['title'] = text[0] if len(text) >= 1 else ""
                            itemt_2['url'] = self.__getCompleteUrl(url[0]) if len(url) >= 1 else "" 
                            print "-> %s:%s" % (itemt_2['title'], itemt_2['url'])
                            key = itemt_2['title']+itemt_2['url']
                            itemt_2['queue_key'] = hashlib.md5(key.encode('utf8')).hexdigest().upper()
                            itemt_2['parent_key'] = itemt['queue_key']
                            itemt_2['isdir'] = 'yes'
                            category_two_items.append(itemt_2)
                                
                            for mc_em_node in mc_dt_node.select("../dd/em/a"):
                                if mc_em_node is not None:
                                    itemt_3 = JdCategoryItem()
                                    text = mc_em_node.select("text()").extract()
                                    itemt_3['title'] = text[0] if len(text) >= 1 else ""
                                    url = mc_em_node.select("@href").extract()
                                    itemt_3['url'] = self.__getCompleteUrl(url[0]) if len(url) >= 1 else ""
                                    print "->  -> %s" % (itemt_3['title'])
                                    key = itemt_3['title']+itemt_3['url']
                                    itemt_3['queue_key'] = hashlib.md5(key.encode('utf8')).hexdigest().upper()
                                    itemt_3['parent_key'] = itemt_2['queue_key']
                                    itemt_3['isdir'] = 'no'
                                    category_thrd_items.append(itemt_3)
        category_items.extend(category_one_items)
        category_items.extend(category_two_items)
        category_items.extend(category_thrd_items)
        return category_items
    
    def __getCompleteUrl(self, url_str):
        url = url_str
        if str is not None:
            url = url_str if _is_valid_url(url_str) else urljoin_rfc(self.baseUrl, url_str)
        return url
    
    
    pass
