#!/usr/bin/python
#encoding:utf8
'''
Merge key\tvalue files，concatenate lines with same key.
Input file already sorted by key.
'''
import sys
from cStringIO import StringIO

if len(sys.argv) != 3:
    print 'Usage:<input> <output>'
    sys.exit(0)

fin = open(sys.argv[1], 'r')
fout = open(sys.argv[2], 'w')

okey = None
buf = StringIO()
no = 0

for line in fin:
    no += 1
    if no % 50000 == 0:
        print ' %d\r' % no,
        sys.stdout.flush()
    parts = line.strip().split('\t', 1)
    if len(parts) != 2:
        continue
    key, value = parts
    value = value.replace('\t', '    ')
    if okey and key != okey:
        fout.write('%s\t%s\n' % (okey, buf.getvalue()))
        buf.truncate(0)
    buf.write(value)
    buf.write('    ')
    okey = key
else:
    if okey:
        fout.write('%s\t%s\n' % (okey, buf.getvalue()))
        buf.truncate(0)

fin.close()
fout.close()
