'''
Created on 2012-1-2

@author: qianmu.lxj
'''
from cyespider.items import CyeProductItem
from libs.CyeFilter import JingdongFilter
from libs.CyeModels import CyeTbReflector, CyeTbRow, ProductRow
from libs.CyeTools import CyeGiftCursor, CyeCursor
from twisted.internet import reactor
import datetime
import random
import time
import sys


def gotCye(datas):
    info = "Got : %s\n" % "/".join([ str(data.id) for data in datas ])
    print info
    for i in datas:
        if i.id == 14:
            print i.__dict__
        
def onInsert(data):
    print 'completed'
    print data
          
def insertCyeTb():
    newItem = CyeTbRow()
    newItem.assignKeyAttr('id', 0)
    newItem.pkey = 'test'+str(random.randint(1, 999))
    newItem.title = 'test'
    newItem.url = 'url'
    newItem.product_img_url = 'product_img_url'
    newItem.product_img = 'product_img'
    newItem.detail = '''
    <ul id="i-detail">
                        <li title="瀹忚揪鐢礢710e">鍟嗗搧鍚嶇О锛氬畯杈剧數S710e</li>
                        <li>鐢熶骇鍘傚锛�a target="_blank" href="http://www.360buy.com/brand/5816.html">HTC</a></li>
                        <li>鍟嗗搧浜у湴锛氫腑鍥藉ぇ闄�/li>
                        <li>鍟嗗搧姣涢噸锛�.38</li>
                        <li id="aeaoofnhgocdbnbeljkmbjdmhbcokfdb-mousedown">涓婃灦鏃堕棿锛�011-4-11 10:58:34</li>
                        <li>浠锋牸涓炬姤锛氬鏋滄偍鍙戠幇鏈夋瘮浜笢浠锋牸鏇翠綆鐨勶紝<a target="_blank" href="http://myjd.360buy.com/pricetip/report/priceReport.action?id=378342">娆㈣繋涓炬姤</a></li>
                        <li>绾犻敊淇℃伅锛氬鏋滄偍鍙戠幇鍟嗗搧淇℃伅涓嶅噯纭紝<a target="_blank" href="http://club.360buy.com/jdvote/skucheck.aspx?skuid=378342&amp;cid1=652&amp;cid2=653&amp;cid3=655">娆㈣繋绾犻敊</a></li>
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
    
def deltaTime(newtime, oldtime, mformat = '%Y-%m-%d %X'):
    newtime = time.strptime(newtime, mformat)
    oldtime = time.strptime(oldtime, mformat)
    
    ndate = datetime.datetime(newtime[0], newtime[1], newtime[2], newtime[3], newtime[4], newtime[5])
    odate = datetime.datetime(oldtime[0], oldtime[1], oldtime[2], oldtime[3], oldtime[4], oldtime[5])
    return (ndate - odate).days

if __name__ == '__main__':
    print sys.getdefaultencoding()
    detail_dat = '''
    <ul id="i-detail">
                        <li title="瀹忚揪鐢礢710e">鍟嗗搧鍚嶇О锛氬畯杈剧數S710e</li>
                        <li>鐢熶骇鍘傚锛�a target="_blank" href="http://www.360buy.com/brand/5816.html">HTC</a></li>
                        <li>鍟嗗搧浜у湴锛氫腑鍥藉ぇ闄�/li>
                        <li>鍟嗗搧姣涢噸锛�.38</li>
                        <li id="aeaoofnhgocdbnbeljkmbjdmhbcokfdb-mousedown">涓婃灦鏃堕棿锛�011-4-11 10:58:34</li>
                        <li>浠锋牸涓炬姤锛氬鏋滄偍鍙戠幇鏈夋瘮浜笢浠锋牸鏇翠綆鐨勶紝<a target="_blank" href="http://myjd.360buy.com/pricetip/report/priceReport.action?id=378342">娆㈣繋涓炬姤</a></li>
                        <li>绾犻敊淇℃伅锛氬鏋滄偍鍙戠幇鍟嗗搧淇℃伅涓嶅噯纭紝<a target="_blank" href="http://club.360buy.com/jdvote/skucheck.aspx?skuid=378342&amp;cid1=652&amp;cid2=653&amp;cid3=655">娆㈣繋绾犻敊</a></li>
                    </ul>
    '''
    
    #testDetail2Model()
    
    print "[cyeTbReflector]"
    d = CyeTbReflector.loadObjectsFrom("cye_tb")
    d.addCallback(gotCye)
    k = []
    if not k:
        print deltaTime('2012-01-01 13:28:33', time.strftime('%Y-%m-%d %X', time.localtime()))
    #insertCyeTb()
    item = CyeProductItem()
    item['last_price'] = '24.00'
    two = '24.00'
    if not (None or two):
        print item['last_price']
    print item['last_price'] is two
    print item.keys()
    
    product_sql = "SELECT * FROM cye_tb WHERE id=%d" % 1
    CyeCursor.execute(product_sql)
    product = CyeCursor.fetchone()
    print type(product[0])
    
    reactor.callLater(7, reactor.stop)
    reactor.run()
    
    
    
    pass



