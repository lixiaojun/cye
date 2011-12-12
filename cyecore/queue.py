# -*- coding: utf-8 -*-
'''
Created on 2011-11-20

@author: lixiaojun
'''
from scrapy.utils.reqser import request_to_dict, request_from_dict
import marshal


class SpiderQueue(object):
    """Per-spider queue abstraction on top of redis using sorted set"""

    def __init__(self, redis_cli, spider, key):
        """Initialize per-spider redis queue

        Parameters:
            redis_cli -- redis connection
            spider -- spider instance
            key -- key for this queue
        """
        self.redis_cli = redis_cli
        self.spider = spider
        self.key = key

    def __len__(self):
        return self.redis_cli.zcard(self.key)

    def push(self, request):
        data = marshal.dumps(request_to_dict(request, self.spider))
        pairs = {data: -request.priority}
        self.redis_cli.zadd(self.key, **pairs)

    def pop(self):
        # use atomic range/remove using multi/exec
        pipe = self.redis_cli.pipeline()
        pipe.multi()
        pipe.zrange(self.key, 0, 0).zremrangebyrank(self.key, 0, 0)
        results, count = pipe.execute()
        if results:
            return request_from_dict(marshal.loads(results[0]), self.spider)

    def clear(self):
        self.redis_cli.delete(self.key)
        
    def getQueue(self, cli, key):
        return cli.smembers(key)
        

