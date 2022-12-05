# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 19:23:38 2022

@author: jayga
"""

from Blockchain import wallet

w = wallet()

a,b = w.get_pair()

print(a,b)

