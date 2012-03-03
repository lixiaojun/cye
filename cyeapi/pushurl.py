'''
Created on 2012-2-25

@author: lixiaojun
'''

from scrapy.conf import settings
import os
import re
import string
import sys
LIB_PATH = os.path.join(os.path.dirname(__file__), '../').replace('\\','/')
sys.path.append(LIB_PATH)
from libs.CyeTools import CyeRedis

class Validation:
    @classmethod
    def isString(cls,varobj):
        return isinstance(varobj, str) or Validation.isUnicode(varobj)
    
    @classmethod
    def isUrl(cls, varobj):
        flag = False
        if cls.isString(varobj):
            rule = '[a-zA-z]+://[^\s]*'
            match = re.match(rule, varobj)
            if match:
                flag = True
        return flag
    
    @classmethod
    def isInt(cls, varobj):
        flag = False
        if cls.isString(varobj):
            rule = '^[1-9][0-9]*$'
            match = re.match(rule, varobj)
            if match:
                flag = True
        return flag
    
    @classmethod
    def isJingdongProduct(cls, varobj):
        flag = False
        if cls.isString(varobj):
            rule = r'http://www.360buy\.com/product/\d+\.[a-zA-Z]+'
            match = re.match(rule, varobj)
            if match:
                flag = True
        return flag

redis_cli = CyeRedis.getInstance()


def pushUrl(url, score=0):
    ret = False
    if Validation.isJingdongProduct(url):
        namespace = 'jingdong'
        update_urls_key = settings.get('REDIS_UPDATE_URLS_KEY', '%s:update') % namespace
        print update_urls_key
        if redis_cli.zadd(update_urls_key, url, score):
            ret = True
    return ret

if __name__ == "__main__":
    print sys.path
    url= None
    score = 0
    arg_cnt = len(sys.argv)
    if arg_cnt > 1:
        url = sys.argv[1]
        if arg_cnt > 2:
            rule = '\.'
            match = re.search(rule, sys.argv[2])
            try:
                if match:
                    score = string.atof(sys.argv[2])
                else:
                    score = string.atoi(sys.argv[2])
            except ValueError:
                pass
        print pushUrl(url, score)
    
