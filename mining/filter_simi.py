#!/usr/bin/python
#encoding:utf8
'''
Filter simi file:
    - convert gindex to gid
    - mutually exclusive goods names
    - max similar goods from the same store

Input:
    m.e. goods name groups (m.e. in the same group, like 半裙,长裙)
    goods_name.kv
    goods_binfo:  shop id
    goods.docinfo
'''
import sys
import os
from common.kvengine import KVEngine, full_path, key_id, write_kv_dict, int_float_dict

def main():
    if len(sys.argv) != 3:
        print 'Usage: <goods_name.csv> <goods_name_me>'
        sys.exit(0)

if __name__ == '__main__':
    main()
