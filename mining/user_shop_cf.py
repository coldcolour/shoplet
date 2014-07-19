#!/user/bin/python
#encoding:utf-8
'''
* cfss, user_favs -> 给每个用户推荐，产生cfus.kv，uid\tsid:weight;
* user_favs -> 每个用户的相似用户，cfuu.kv, uid\tuid:weight
'''
import sys
from common.kvengine import KVEngine, full_path, key_id, write_kv_dict
from common.utils import norm_dot_product, normalize
import math

def compute_cfss():
    '''
    计算shop-shop相似关系矩阵。
    Input:
        shop_actu：用户对店铺做的动作
    Process: 
        取用户动作表示的shop向量，计算向量点积。
    Output:
        shop-shop 相似关系，cfss.kv
    '''
    # shop_actu -> shop-shop关系矩阵，并保存cfss.kv，shop\tshop:weight;
    kvg = KVEngine()
    kvg.load([full_path('shop_actu.kv')])

    # get normialized vectors
    shop_users = {}
    skeys = kvg.keymatch('S\d+_ACTU')
    for skey in skeys:
        sid = key_id(skey)
        vector = dict([(int(key), float(value)) for (key, value) in kvg.getd(skey).items() if key and value])
        # tailor to top 20
        items = vector.items()
        items.sort(key=lambda x:x[1], reverse=True)
        items = items[:20]
        vector = dict(items)
        normalize(vector)
        shop_users[sid] = vector

    # similarity calculation
    shop_similarity = {}
    sids = shop_users.keys()
    sids.sort()
    l = len(sids)
    print "Calculating similarity matrix, total %d..." % l
    for i in range(l):
        if i % 1000 == 0:
            print "%d" % i
            sys.stdout.flush()
        for j in range(i+1, l):
            sim = norm_dot_product(shop_users[sids[i]], shop_users[sids[j]])
            if abs(sim) < 1e-5:
                continue
            shop_similarity.setdefault(sids[i], {})[sids[j]] = sim
            shop_similarity.setdefault(sids[j], {})[sids[i]] = sim

    # save as kvfile
    write_kv_dict(shop_similarity, 'S%s_CFSIMS', 'cfss.kv')

def compute_cfus():
    '''
    计算给用户推荐的店铺列表。
    Input: 
        cfss: 店铺关系
        user_favu: 用户关注店铺
        user_actu: 用户有动作店铺
    Process:
        从用户直接相关店铺出发，找这些店铺的相关店铺，再过滤。
    Output:
        存储CF算法产生的给用户推荐的店铺列表。cfus.kv
    '''
    pass

def compute_cfuu():
    '''
    计算用户之间的相似关系。
    Input:
        user_acts: 用户对店铺所做动作
    Process: 
        取用户对店铺动作向量，计算点积
    Output:
        user-user关系，cfuu.kv
    '''
    pass

def main():
    compute_cfss()
    compute_cfus()
    compute_cfuu()

if __name__ == '__main__':
    main()

