# -*- coding: utf-8 -*-
'''
Created on 2011-11-26

@author: lixiaojun
'''

from libs.cyetools import CyeRedis
import json
import redis


def main():
    redis_cli = CyeRedis.getInstance()
    while True:
        source, data = redis_cli.brpop(["dmoz:items"])
        item = json.loads(data)
        try:
            print u"Processing: %(name)s <%(link)s>" % item
        except KeyError:
            print u"Error procesing: %r" % item


if __name__ == '__main__':
    main()
