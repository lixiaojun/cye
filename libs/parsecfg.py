# -*- coding: utf-8 -*-
'''
Created on 2011-11-19

@author: lixiaojun
'''
import json

class CyeCfg(object):
    def __init__(self):
        
        pass
    
    def getCfgFromJson(self, argv):
        cfg_dict = {}
        if argv is not None:
            cfg_dict = json.JSONDecoder().decode(argv)
        return cfg_dict
    
    pass


if __name__ == '__main__':
    
    job_opt = {"job_id":10, "url":"http://www.360buy.com/products/652-653-655.html", "queue_key":"076AB2175C0D2F24BE8C157731D03C1B"}
    s = json.JSONEncoder().encode(job_opt)
    ccfg = CyeCfg()
    print ccfg.getCfgFromJson(s)
    pass