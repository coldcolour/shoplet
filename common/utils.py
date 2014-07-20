#!/usr/bin/python
#encoding:utf8
import os
import re
import math

def normalize(d):
    """
    normalize a dict, key -> value of number
    """
    m = 0.0
    for w in d.values():
        m += w * w
    m = math.sqrt(m)
    if abs(m) >= 1e-5:
        for i in d:
            d[i] /= m

def norm_dot_product(v, w):
    """
    dot product for two dicts, both already normalized
    """
    s = 0.0
    for vv in v:
        if vv in w:
            s += v[vv] * w[vv]
    return s

