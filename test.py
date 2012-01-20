'''
Created on 2012-1-2

@author: qianmu.lxj
'''
from cyespider.items import CyeProductItem
from libs.CyeFilter import JingdongFilter
from libs.pytesser.pytesser import image_to_string
import Image
import os
import sys
import time

def testOrc():
    ORC_PATH = os.path.join(os.path.dirname(__file__), 'libs/pytesser').replace('\\','/')
    full_path = ORC_PATH + "/test.png"
    im = Image.open(full_path)
    text = image_to_string(im)
    print "testOrc: %s" % text

if __name__ == '__main__':
    print sys.getdefaultencoding()
    
    testOrc()
    
    pass



