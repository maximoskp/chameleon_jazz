# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 15:30:30 2022

@author: user
"""

import kern_converters as kc
import os

file_name = 'kern_files' + os.sep + 'kern_reconstructed.krn'

p = kc.kern2py(file_name)
s = kc.kern2string(file_name)
print(p)
print(s)