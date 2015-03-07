#-*- coding: utf-8 -*-

import os



def encrypt(self,_Dialog):
    aes_key = os.urandom(32)
    out_filename = filepath+'.enc'
