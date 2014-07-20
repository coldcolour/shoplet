#!/user/bin/python
#encoding:utf-8
'''
'''
import sys
from common.kvengine import KVEngine, full_path, key_id, write_kv_dict
from common.utils import norm_dot_product, normalize
import math

def compute_cfgg():
    '''
    计算goods-goods相似关系矩阵。
    Input:
        user_actg.kv -> goods_actu.kv：用户对店铺做的动作
    Process: 
        取用户动作表示的goods向量，计算向量点积。
    Output:
        goods-goods 相似关系，cfss.kv
    '''
    kvg = KVEngine()
    kvg.load([full_path('goods_actu.kv')])

    # get normialized vectors
    goods_users = {}
    gkeys = kvg.keymatch('G\d+_ACTU')
    for gkey in gkeys:
        gid = key_id(gkey)
        vector = dict([(int(key), float(value)) for (key, value) in kvg.getd(gkey).items() if key and value])
        # tailor to top 20
        items = vector.items()
        items.sort(key=lambda x:x[1], reverse=True)
        items = items[:20]
        vector = dict(items)
        normalize(vector)
        goods_users[gid] = vector

    # similarity calculation
    goods_similarity = {}
    gids = goods_users.keys()
    gids.sort()
    l = len(gids)
    print "Calculating goods-goods similarity matrix, total %d..." % l
    for i in range(l):
        if i % 100 == 0:
            print "%d" % i
            sys.stdout.flush()
        for j in range(i+1, l):
            sim = norm_dot_product(goods_users[gids[i]], goods_users[gids[j]])
            if abs(sim) < 1e-5:
                continue
            goods_similarity.setdefault(gids[i], {})[gids[j]] = sim
            goods_similarity.setdefault(gids[j], {})[gids[i]] = sim

    # save as kvfile
    write_kv_dict(goods_similarity, 'G%s_CFSIMG', 'cfgg.kv')

def compute_cfug():
    '''
    计算给用户推荐的商品的列表。
    Input: 
        cfgg：商品之间的关系
        user_favg: 用户收藏的商品
        user_actg: 用户有动作商品
    Process:
        从用户直接相关商品出发，找这些商品的相关商品，再过滤。
    Output:
        存储CF算法产生的给用户推荐的商品列表 -> cfug.kv
    '''
    pass

def compute_cfuu():
    '''
    计算用户之间的相似关系。
    Input:
        user_actg: 用户对商品所做动作
    Process: 
        取用户对商品动作向量，计算点积
    Output:
        user-user关系，goodscfuu.kv
    '''
    pass

def main():
    compute_cfgg()
    compute_cfug()
    compute_cfuu()

if __name__ == '__main__':
    main()

