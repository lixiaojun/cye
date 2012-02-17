'''
Created on 2012-2-16

@author: lixiaojun
'''
from libs.CyeTools import MygiftSession
from scrapy.conf import settings
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from sqlalchemy.orm import scoped_session
import re
#from fooSpider.pipelines import FooPipeline
#settings.overrides['ITEM_PIPELINES'] = ['fooSpider.pipelines.FooImagePipeline']

class JingdongUpdateSpider(BaseSpider):
    name = "jingdong_update"
    namespace = "jingdong"
    base_url = "http://www.360buy.com"
    start_urls = ["http://www.360buy.com"]
    
    def __init__(self, **kw):
        self._init_urls()
        super(JingdongUpdateSpider, self).__init__(self.name, **kw)
        
    def _init_urls(self):
        self.session = scoped_session(MygiftSession)
        self.urls_key = settings.get('REDIS_URLS_KEY', '%s:urls') % self.namespace
        

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select('//div[@id="plist"]/ul[@class="list-h"]/li/div[@class="p-img"]/a/@href').extract()
        #print links
        for link in links:
            #print link
            request = Request(link, callback=self.parse_post)
            yield request

        link = hxs.select('//a[@class="next"]/@href').extract()[0]
        url = self.base_url+link
        #print "next url:"+url
        request = Request(url, callback=self.parse)
        yield request

    def parse_post(self, response):
        pass

    def parse_response(self, response):
        pass

    def striphtml(self, data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)
