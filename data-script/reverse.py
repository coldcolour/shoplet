#!/usr/bin/python
#encoding:utf8
'''
Reverse a key-value file.
'''
import os
import sys
import re

RE_DIGITS = re.compile('\d+')

def main():
    if len(sys.argv) != 3:
        print 'Usage:<kv file> <pattern XX for id>'
        sys.exit(0)
    inf = open(sys.argv[1], 'r')
    pat = sys.argv[2]
    d = {}
    for line in inf:
        parts = line.strip().split('\t')
        if len(parts) != 2:
            continue
        rid = re.search(RE_DIGITS, parts[0]).group()
        cols = parts[1].split(';')
        for col in cols:
            parts = col.split(':')
            if len(parts) != 2:
                continue
            k, v = parts
            d.setdefault(k, {})[rid] = v
    inf.close()
    for key in d:
        print '%s\t%s' % (pat.replace('XX', key), ';'.join(['%s:%s' % item for item in d[key].items()]))

if __name__ == '__main__':
    main()
