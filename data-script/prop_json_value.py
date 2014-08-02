#!/usr/bin/python
#encoding:utf8
'''
convert goods_prop.csv's json string to values in UTF8
'''
import sys
import json

if len(sys.argv) != 2:
    print 'Usage: <input file name>'
    sys.exit(0)

fin = open(sys.argv[1])
for line in fin:
    parts = line.strip().split('\t')
    gid, jsonstr = parts
    jsonstr = jsonstr.replace('\\\\', '\\')
    obj = json.loads(jsonstr)
    print '%s\t%s' % (gid, ';'.join([v.encode('utf8', 'ignore') for v in obj.values()]))
fin.close()
