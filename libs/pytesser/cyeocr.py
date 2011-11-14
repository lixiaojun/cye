# -*- coding: utf-8 -*-
'''
Created on 2011-10-29

@author: lixiaojun
'''

from libs.pytesser.pytesser import image_to_string
import Image
import os

class CyeOcr(object):
    
    im = None
    text = None
    '''
    图片预处理，上下左右需剪切的像素
    '''
    CUT_LEFT = 20
    CUT_RIGHT = 3
    CUT_TOP = 0
    CUT_BOOM = 0
    
    def __init__(self, img_path):
        if os.path.exists(img_path):
            self.im = Image.open(img_path)
            self.im.load()
            self.toText()
            
    def toText(self):
        self.im = self.preprocess(self.im)
        if len(self.im.split()) == 4:
            r,g,b,a = self.im.split()
            im = Image.merge("RGB", (r,g,b))
            self.text = image_to_string(im)
    
    def getText(self):
        return self.text
    
    def preprocess(self, im):
        
        out = im
        if im is not None:
            box = (self.CUT_LEFT, self.CUT_TOP, im.size[0] - self.CUT_RIGHT, im.size[1] - self.CUT_BOOM)
            out = im.crop(box)
        return out
    
    def setBox(self, l, r, t, b):
        if type(l) == int and l >= 0:
            self.CUT_LEFT = l
        else:
            self.CUT_LEFT = 0
        if type(r) == int and r >= 0:
            self.CUT_RIGHT = r
        else:
            self.CUT_RIGHT = 0
        if type(t) == int and t >= 0:
            self.CUT_TOP = t
        else:
            self.CUT_TOP = 0
        if type(b) == int and b >= 0:
            self.CUT_BOOM = b
        else:
            self.CUT_BOOM = 0
    pass