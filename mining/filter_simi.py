#!/usr/bin/python
#encoding:utf8
'''
Simi file filtering tool

Input:
    goods.simi: gidx -> gidx:weight ...
    goods.docinfo: gidx -> gid
    goods_name.kv: gid -> name
    goods_binfo: bid -> shop id (by KVEngine)
    name.me: mutually exclusive goods name groups (m.e. in the same group, like 半裙,长裙)

Process:
    convert gindex to gid
    mutually exclusive goods names
    max similar goods from the same store

Output:
    filtered goods.simi: gid -> gid:weight ...

'''
import sys
import os
from common.kvengine import KVEngine, full_path
MAX_SAME_SHOP = 5

def read_docinfo(fname):
    gindex2id = {}
    with open(fname, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) != 2:
                continue
            index = int(parts[0])
            gid = int(parts[1])
            #gid2index[gid] = index
            gindex2id[index] = gid
    return gindex2id

def read_simi(fname, gidx2id):
    gid2simi = {}
    with open(fname, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            gidx = int(parts[0])
            gid = gidx2id[gidx]
            for part in parts[1:]:
                subparts = part.split(':')
                if len(subparts) != 2:
                    continue
                rgidx = int(subparts[0])
                rgid = gidx2id[rgidx]
                weight = float(subparts[1])
                gid2simi.setdefault(gid, {})[rgid] = weight
    return gid2simi

def read_name(fname):
    gid2name = {}
    with open(fname, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) != 2:
                continue
            gid = int(parts[0])
            name = parts[1]
            gid2name[gid] = name
    return gid2name

def read_me(fname):
    '''
    五分裤|5分裤 七分裤|7分裤 八分裤|8分裤 九分裤|9分裤
    裙裤 长裙 短裙 中裙
    '''
    name_me = {}
    with open(fname, 'r') as f:
        bigno = 0
        for line in f:
            parts = line.strip().split()
            for smallno in range(len(parts)):
                subparts = parts[smallno].split('|')
                for spart in subparts:
                    name_me[spart] = (bigno, smallno)
            bigno += 1
    return name_me

def same_shop_limit(gid2simi, kvg):
    global MAX_SAME_SHOP

    for no, gid in enumerate(gid2simi):
        if no % 10000 == 0:
            print '%d ' % no,
            sys.stdout.flush()
        vector = gid2simi[gid]
        gshopid = get_shop_id(gid, kvg)
        gshopcnt = 0
        items = vector.items()
        items.sort(reverse=True, key=lambda x:x[1])
        remain_items = []
        for item in items:
            rgshopid = get_shop_id(item[0], kvg)
            if rgshopid == gshopid:
                gshopcnt += 1
                if gshopcnt > MAX_SAME_SHOP:
                    #print '%d-%d removed by same shop' % (gid, item[0])
                    #sys.stdout.flush()
                    continue
            remain_items.append(item)
        gid2simi[gid] = dict(remain_items)
    else:
        print

def get_me_words(gname, name_me):
    return [key for key in name_me if key in gname]

def get_shop_id(gid, kvg):
    try:
        return int(kvg.getk('G%d-BINFO' % gid, 'shop'))
    except ValueError:
        return -1

def me(gmewords, rgmewords):
    mewords = []
    mewords.extend(gmewords)
    mewords.extend(rgmewords)
    mewords = set(gmewords)
    if len(mewords) != len(set([i[0] for i in mewords])):
        # 如果unique bigno数不等于总数，判断同一bigno有多个smallno，需要互斥
        return True
    else:
        return False

def mutually_exclusive_names(gid2simi, gid2name, name_me):
    for no, gid in enumerate(gid2simi):
        if no % 10000 == 0:
            print '%d ' % no,
            sys.stdout.flush()
        vector = gid2simi[gid]
        gname = gid2name[gid]
        gmewords = get_me_words(gname, name_me)
        if not gmewords:
            continue
        items = vector.items()
        remain_items = []
        for item in items:
            rgname = gid2name[item[0]]
            rgmewords = get_me_words(rgname, name_me)
            if not rgmewords:
                remain_items.append(item)
            else:
                if me(gmewords, rgmewords):
                    print '%d-%d removed by me' % (gid, item[0])
                    sys.stdout.flush()
                    continue
                else:
                    remain_items.append(item)
        gid2simi[gid] = dict(remain_items)
    else:
        print

def output(fname, gid2simi):
    with open(fname, 'w') as f:
        for gid in gid2simi:
            f.write('%d %s\n' % (gid, ' '.join(['%d:%.4f' % item for item in gid2simi[gid].items()])))

def main():
    if len(sys.argv) != 6:
        print 'Usage: <goods.simi> <goods.docinfo> <goods.name> <name.me> <goods.simi.output>'
        sys.exit(0)

    print 'docinfo...'; sys.stdout.flush()
    gidx2id = read_docinfo(sys.argv[2])
    print 'simi...'; sys.stdout.flush()
    gid2simi = read_simi(sys.argv[1], gidx2id)
    print 'name...'; sys.stdout.flush()
    gid2name = read_name(sys.argv[3])
    print 'name.me...'; sys.stdout.flush()
    name_me = read_me(sys.argv[4])
    kvg = KVEngine()
    print 'binfo...'; sys.stdout.flush()
    kvg.load([full_path('goods_binfo.kv')])

    print 'shop limit...'; sys.stdout.flush()
    same_shop_limit(gid2simi, kvg)
    print 'mutually_exclusive_names...'; sys.stdout.flush()
    mutually_exclusive_names(gid2simi, gid2name, name_me)
    #todo: 童装与非童装互斥

    print 'output...'; sys.stdout.flush()
    output(sys.argv[5], gid2simi)

if __name__ == '__main__':
    main()
