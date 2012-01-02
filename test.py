# -*- coding: utf-8 -*-
'''
Created on 2012-1-2

@author: qianmu.lxj
'''
from cyespider.items import CyeProductItem
from libs.CyeFilter import JingdongFilter
from libs.CyeModels import CyeTbReflector, CyeTbRow, ProductRow
from twisted.internet import reactor
import random
import time

def gotCye(datas):
    info = "Got : %s\n" % "/".join([ data.pkey for data in datas ])
    print info
        
def onInsert(data):
    print 'completed'
    print data
          
def insertCyeTb():
    newItem = CyeTbRow()
    newItem.assignKeyAttr('id', 0)
    newItem.assignKeyAttr('pkey', 'test'+str(random.randint(1, 999)))
    newItem.title = 'test'
    newItem.url = 'url'
    newItem.product_img_url = 'product_img_url'
    newItem.product_img = 'product_img'
    newItem.detail = '''
    <ul id="i-detail">
                        <li title="宏达电S710e">商品名称：宏达电S710e</li>
                        <li>生产厂家：<a target="_blank" href="http://www.360buy.com/brand/5816.html">HTC</a></li>
                        <li>商品产地：中国大陆</li>
                        <li>商品毛重：0.38</li>
                        <li id="aeaoofnhgocdbnbeljkmbjdmhbcokfdb-mousedown">上架时间：2011-4-11 10:58:34</li>
                        <li>价格举报：如果您发现有比京东价格更低的，<a target="_blank" href="http://myjd.360buy.com/pricetip/report/priceReport.action?id=378342">欢迎举报</a></li>
                        <li>纠错信息：如果您发现商品信息不准确，<a target="_blank" href="http://club.360buy.com/jdvote/skucheck.aspx?skuid=378342&amp;cid1=652&amp;cid2=653&amp;cid3=655">欢迎纠错</a></li>
                    </ul>
    '''
    newItem.utime = time.strftime('%Y-%m-%d %X', time.localtime())
    
    CyeTbReflector.insertRow(newItem).addCallback(onInsert)

def testDetail2Model():
    detail = JingdongFilter.handleDetail(detail_dat)
    print detail
    
    prow = ProductRow()
    
    def detail2Model(detail, model):
        for key in detail.keys():
            setattr(model, key, detail[key])
    
    def printRow(row):
        print row.__dict__
    
    detail2Model(detail, prow)
    printRow(prow)
    
    item = CyeProductItem()
    row_keyattrs = [attr for attr, t in prow.rowKeyColumns]
    print row_keyattrs

if __name__ == '__main__':
    detail_dat = '''
    <ul id="i-detail">
                        <li title="宏达电S710e">商品名称：宏达电S710e</li>
                        <li>生产厂家：<a target="_blank" href="http://www.360buy.com/brand/5816.html">HTC</a></li>
                        <li>商品产地：中国大陆</li>
                        <li>商品毛重：0.38</li>
                        <li id="aeaoofnhgocdbnbeljkmbjdmhbcokfdb-mousedown">上架时间：2011-4-11 10:58:34</li>
                        <li>价格举报：如果您发现有比京东价格更低的，<a target="_blank" href="http://myjd.360buy.com/pricetip/report/priceReport.action?id=378342">欢迎举报</a></li>
                        <li>纠错信息：如果您发现商品信息不准确，<a target="_blank" href="http://club.360buy.com/jdvote/skucheck.aspx?skuid=378342&amp;cid1=652&amp;cid2=653&amp;cid3=655">欢迎纠错</a></li>
                    </ul>
    '''
    
    testDetail2Model()
    
    print "[cyeTbReflector]"
    d = CyeTbReflector.loadObjectsFrom("cye_tb")
    
    #d.addCallback(gotCye)
    
    #insertCyeTb()
    
    #reactor.callLater(7, reactor.stop)
    #reactor.run()
    pass
