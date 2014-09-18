#!/usr/bin/python
#encoding:utf8
'''
生成相似商品的demo html。

Input:
    goods.simi: gindex gindex:weight ...
    goods.docinfo: translate gindex -> gid
    goods binfo: title, imgurl, taobaourl, ...
Output:
    html file
'''
import sys
import random
from cStringIO import StringIO
from common.kvengine import KVEngine, full_path, key_id, write_kv_dict, int_float_dict

def read_idx_map(fname):
    gidx2gid = {}
    finput = open(fname, 'r')
    for line in finput:
        parts = line.strip().split(',')
        if len(parts) != 2:
            continue
        gidx2gid[int(parts[0])] = int(parts[1])
    finput.close()
    return gidx2gid

def read_simi(fname):
    goods_simi = {}
    finput = open(fname, 'r')
    for line in finput:
        parts = line.strip().split()
        gid = int(parts[0])
        if gid == -1:
            continue
        else:
            goods_simi[gid] = {}
        for part in parts[1:]:
            subparts = part.split(':')
            if len(subparts) != 2:
                continue
            rgid = int(subparts[0])
            weight = float(subparts[1])
            goods_simi[gid][rgid] = weight
    finput.close()
    return goods_simi

def read_goods_simi(fname, gidx2gid):
    goods_simi = {}
    finput = open(fname, 'r')
    for line in finput:
        parts = line.strip().split()
        gid = gidx2gid.get(int(parts[0]), -1)
        if gid == -1:
            continue
        else:
            goods_simi[gid] = {}
        for part in parts[1:]:
            subparts = part.split(':')
            if len(subparts) != 2:
                continue
            rgid = gidx2gid.get(int(subparts[0]), -1)
            weight = float(subparts[1])
            goods_simi[gid][rgid] = weight
    finput.close()
    return goods_simi

def ginfo(kvg, gid):
    key = 'G%d-BINFO' % gid
    if key not in kvg:
        return 'unknown', '', ''
    title = kvg.getk(key, 'name')
    imgurl = kvg.getk(key, 'imgurl')
    taobaourl = "http://item.taobao.com/item.htm?id=%s" % kvg.getk(key, 'tbid')
    return title, imgurl, taobaourl

def main_snippet(case, gid, title, imgurl, taobaourl):
    if not (gid and title and imgurl and taobaourl):
        return ''
    else:
        return '<div style="width:300px;clear:both;border-style:dashed;border-color:red;border-width:thick;">Case #%d <a href="%s" target="_blank"><img  title="%s" src="%s" style="width:300px"></a><br/>%s<br/>商品id：%d</div>\n' % (case, taobaourl, title, imgurl, title, gid)

def sub_snippet(subcase, gid, title, imgurl, taobaourl, weight):
    if not (title and imgurl and taobaourl):
        return ''
    else:
        return '<div style="width:200px;height:400px;float:left;border-style:dashed;border-color:grey;border-width:thin;">Match #%d <a href="%s" target="_blank"><img title="%s" src="%s" style="width:200px"></a><br/>%s<br/>商品id：%d<br/>相似度：%.4f</div>\n' % (subcase, taobaourl, title, imgurl, title, gid, weight)

def main():
    if len(sys.argv) != 4:
        print 'Usage: <goods.simi> <goods.docinfo> <output.html>'
        sys.exit(0)

    #gidx2gid = read_idx_map(sys.argv[2])
    #goods_simi = read_goods_simi(sys.argv[1], gidx2gid) #gid -> gid -> weight
    goods_simi = read_simi(sys.argv[1])
    kvg = KVEngine()
    kvg.load([full_path('goods_binfo.kv')])

    html = StringIO()
    html.write('<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /></head>')

    case = 0
    for gid in goods_simi:
        title, imgurl, taobaourl = ginfo(kvg, gid)
        html.write(main_snippet(case, gid, title, imgurl, taobaourl))
        case += 1
        items = goods_simi[gid].items()
        items.sort(key=lambda x:x[1], reverse=True)
        for subcase, item in enumerate(items):
            rgid, weight = item
            rtitle, rimgurl, rtaobaourl = ginfo(kvg, rgid)
            html.write(sub_snippet(subcase, rgid, rtitle, rimgurl, rtaobaourl, weight))
            subcase += 1
            if subcase >= 10:
                break

    open(sys.argv[3], 'w').write(html.getvalue())

if __name__ == '__main__':
    main()

