#!/usr/bin/python
#encoding:utf8
'''
抽样商品，生成HTML，展示该商品的相关商品（图片与链接）
Input: cfgg.kv, goods_binfo.kv
'''
import sys
import random
from cStringIO import StringIO
from common.kvengine import KVEngine, full_path, key_id, write_kv_dict, int_float_dict

def item_snippet(kvg, key, items):
    buf = StringIO()
    imgurl = kvg.getk('G%d-BINFO' % key_id(key), 'imgurl')
    if not imgurl:
        return ''
    itemurl = "http://item.taobao.com/item.htm?id=%s" % kvg.getk('G%d-BINFO' % key_id(key), 'tbid')
    name = kvg.getk('G%d-BINFO' % key_id(key), 'name')
    buf.write('<div style="clear:both;border-style:dashed;border-color:grey;border-width:thin;"><a href="%s" target="_blank"><img  title="%s" src="%s" style="width:300px"></a></div>\n' % (itemurl, name, imgurl))
    for item in items:
        key, weight = item
        imgurl = kvg.getk('G%s-BINFO' % key, 'imgurl')
        name = kvg.getk('G%s-BINFO' % key, 'name')
        itemurl = "http://item.taobao.com/item.htm?id=%s" % kvg.getk('G%s-BINFO' % key, 'tbid')
        buf.write('<div style="float:left;border-style:dashed;border-color:grey;border-width:thin;"><a href="%s" target="_blank"><img title="%s" src="%s" style="width:150"></a></div>\n' % (itemurl, name, imgurl))
    return buf.getvalue()

def main():
    kvg = KVEngine()
    kvg.load([full_path('cfgg.kv')])
    kvg.load([full_path('goods_binfo.kv')])
    keys = kvg.keymatch('G\d+_CFSIMG')
    sample_keys = random.sample(keys, 50)
    html = StringIO()
    html.write('<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /></head>')

    for key in sample_keys:
        similar_goods = int_float_dict(kvg.getd(key))
        items = similar_goods.items()
        items.sort(reverse=True, key=lambda x:x[1])
        items = [item for item in items if ('G%s-BINFO' % item[0]) in kvg][:10]
        html.write(item_snippet(kvg, key, items))

    open('a.html', 'w').write(html.getvalue())

if __name__ == '__main__':
    main()

