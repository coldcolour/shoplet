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
import math
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
            name = parts[1].lower()
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

def get_goods_price(kvg, gid):
    try:
        return float(kvg.get('G%d-PRICE' % gid))
    except ValueError:
        return -1.

def same_shop_limit(gid2simi, kvg):
    global MAX_SAME_SHOP

    for no, gid in enumerate(gid2simi):
        if no % 10000 == 0:
            print '%d ' % no,
            sys.stdout.flush()
        vector = gid2simi[gid]
        gshopid = get_shop_id(gid, kvg)
        #print '*%d' % gshopid
        gshopcnt = 0
        items = vector.items()
        items.sort(reverse=True, key=lambda x:x[1])
        remain_items = []
        for item in items:
            rgshopid = get_shop_id(item[0], kvg)
            #print '%d' % rgshopid
            if rgshopid == gshopid:
                gshopcnt += 1
                if gshopcnt > MAX_SAME_SHOP:
                    #print '%d-%d removed by same shop' % (gid, item[0])
                    #sys.stdout.flush()
                    continue
                else:
                    remain_items.append((item[0], item[1] * 0.35)) # 同店商品相似度降权
                    #print 'same shop %d %.2f -> %.2f' % (item[0], item[1], item[1] * 0.35)
            else:
                remain_items.append(item)
        gid2simi[gid] = dict(remain_items)
    else:
        print

def get_me_words(gname, name_me):
    keys = [key for key in name_me if key in gname]
    if '童' not in keys:
        keys.append('非童')
    if '中年' not in keys or '中老年' not in keys:
        keys.append('非中老年')
    return keys

def get_shop_id(gid, kvg):
    try:
        return int(kvg.getk('G%d-BINFO' % gid, 'shop'))
    except ValueError:
        return -1

def me(gmewords, rgmewords, name_me):
    mewords = []
    mewords.extend(gmewords)
    mewords.extend(rgmewords)
    mewords = set(mewords)
    if len(mewords) != len(set([name_me[i][0] for i in mewords])):
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
                #import pdb; pdb.set_trace()
                if me(gmewords, rgmewords, name_me):
                    #print '%d-%d removed by me' % (gid, item[0])
                    #sys.stdout.flush()
                    continue
                else:
                    remain_items.append(item)
        gid2simi[gid] = dict(remain_items)
    else:
        print

def price_adj(gid2simi, kvg):
    '''
    相似商品价格如果在±10%, ±20%, ±30%，做1.5, 1.2, 1.1提权
    '''
    for no, gid in enumerate(gid2simi):
        gprice = get_goods_price(kvg, gid)
        if gprice == -1:
            continue

        if no % 10000 == 0:
            print '%d ' % no,
            sys.stdout.flush()

        for rgid in gid2simi[gid]:
            weight = gid2simi[gid][rgid]
            rgprice = get_goods_price(kvg, rgid)
            if rgprice == -1:
                continue
            delta = int(abs(gprice - rgprice) / gprice * 10)
            if delta == 0 or delta == 1:
                weight *= 2.0
            elif delta == 2:
                weight *= 1.2
            elif delta == 3:
                weight *= 1.1
            elif delta >= 5:
                weight *= 0.5
            else:
                pass
            gid2simi[gid][rgid] = weight

def output(fname, gid2simi):
    with open(fname, 'w') as f:
        for gid in gid2simi:
            if gid2simi[gid]:
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
    kvg.load([full_path('goods_price.kv')])

    print 'shop limit...'; sys.stdout.flush()
    same_shop_limit(gid2simi, kvg)
    print 'mutually_exclusive_names...'; sys.stdout.flush()
    mutually_exclusive_names(gid2simi, gid2name, name_me)
    print 'price adjustment...'; sys.stdout.flush()
    price_adj(gid2simi, kvg)

    print 'output...'; sys.stdout.flush()
    output(sys.argv[5], gid2simi)

if __name__ == '__main__':
    main()
