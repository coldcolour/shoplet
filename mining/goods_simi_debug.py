#!/usr/local/bin/python
#encoding:utf8
'''
Input:
    goods.dic: id -> word
    goods.docinfo: gid -> index
    goods.wv: gindex -> word vector
    goods_category.csv: gid -> categories
    goods_txt: gid -> text
Process:
    read files and make,
    gid -> index
    gid -> cat
    gid -> text
    gid -> index (w/ word name)
Output:
    id, id ->
    id: xxxxx
    cat: xxxxx
    text: xxxx
    index: xx:xx xx:xx xx:xx ...
    --------------------------
    id: xxxxx
    cat: xxxxx
    text: xxxx
    index: xx:xx xx:xx xx:xx ...
    --------------------------
    similarity: xxxxx
    match:
        xx: 00x00=0000 xx: 00x00=0000 ....

    id -> ...
'''
import os
import sys
from subprocess import check_output

wid2word = {}
gid2index = {}
gindex2id = {}
gid2vector = {}
gid2cat = {}
gid2txt = {}

def read_dic(fname):
    print 'read word dic....',;sys.stdout.flush()
    no = 0
    global wid2word
    with open(fname, 'r') as f:
        for line in f:
            word = line.strip()
            wid2word[no] = word
            no += 1
    print 'done'; sys.stdout.flush()

def read_docinfo(fname):
    print 'read docinfo...', ;sys.stdout.flush()
    global gid2index, gindex2id
    with open(fname, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) != 2:
                continue
            index = int(parts[0])
            gid = int(parts[1])
            gid2index[gid] = index
            gindex2id[index] = gid
    print 'done'; sys.stdout.flush()

def read_wordvector(fname):
    print 'read word vector...',;sys.stdout.flush()
    global gindex2id, wid2word, gid2vector
    with open(fname, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            gidx = int(parts[0])
            gid = gindex2id[gidx]
            for part in parts[1:]:
                subparts = part.split(':')
                if len(subparts) != 2:
                    continue
                wid= int(subparts[0])
                word = wid2word[wid]
                weight = float(subparts[1])
                gid2vector.setdefault(gid, []).append((wid, word, weight))
    print 'done'; sys.stdout.flush()

def read_category(fname):
    print 'read category...',;sys.stdout.flush()
    global gid2cat
    with open(fname, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) != 3:
                continue
            gid = int(parts[0])
            category = parts[2].split(':')[0]
            gid2cat.setdefault(gid, set()).add(category)
    print 'done'; sys.stdout.flush()

def read_text(fname):
    print 'read text...',;sys.stdout.flush()
    global gid2txt
    with open(fname, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) != 2:
                continue
            gid = int(parts[0])
            text = parts[1]
            gid2txt[gid] = text
    print 'done'; sys.stdout.flush()

def print_goods_info(gid, fname=''):
    print 'id: %d' % gid
    print 'index: %d' % gid2index[gid]
    print 'category: %s' % ','.join(gid2cat.get(gid, set('')))
    text = check_output('grep %d %s | head -1' % (gid, fname), shell=True)
    #text = gid2txt[gid]
    print 'text: %s' % text.strip()
    print 'index: %s' % ' '.join(['%s:%.4f' % (v[1], v[2]) for v in gid2vector[gid]])
    print '-' * 80

def print_goods_match(ida, idb):
    print 'match:'
    sim = 0.0
    va = dict([(v[1], v[2]) for v in gid2vector[ida]])
    vb = dict([(v[1], v[2]) for v in gid2vector[idb]])
    for i in va:
        if i in vb:
            print '\t%s: %.4f x %.4f = %.4f' % (i, va[i], vb[i], va[i] * vb[i])
            sim += va[i] * vb[i]
    print 'similarity: %.4f' % sim
    print '-' * 80

def main():
    if len(sys.argv) != 6:
        print 'Usage: <goods.dic> <goods.docinfo> <goods.wv> <goods.category> <goods.txt>'
        sys.exit(0)

    read_dic(sys.argv[1])
    read_docinfo(sys.argv[2])
    read_wordvector(sys.argv[3])
    read_category(sys.argv[4])
    #read_text(sys.argv[5])

    while True:
        user_input = raw_input('Query("gid,gid" or "gid"): ')
        user_input = user_input.strip()
        parts = user_input.split(',')
        try:
            if len(parts) == 1:
                ida = int(parts[0].strip())
                print_goods_info(ida, fname=sys.argv[5])
            elif len(parts) == 2:
                ida = int(parts[0].strip())
                idb = int(parts[1].strip())
                print_goods_info(ida, fname=sys.argv[5])
                print_goods_info(idb, fname=sys.argv[5])
                print_goods_match(ida, idb)
            else:
                print 'Invalid input!'
        except ValueError:
            print 'Invalid input!'

if __name__ == '__main__':
    main()
