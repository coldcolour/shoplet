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
    print "Calculating shop-shop similarity matrix, total %d..." % l
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
    kvg = KVEngine()
    kvg.load([full_path('cfss.kv')])
    kvg.load([full_path('user_favs.kv')])
    kvg.load([full_path('user_actu.kv')])
    kvg.load([full_path('shop_binfo.kv')])

    # get shop_similarity
    keys = kvg.keymatch('S\d+_CFSIMS')
    shop_similarity = dict([(int(key), dict([(int(k), float(v)) for (k, v) in kvg.getd(key).items()])) for key in keys])

    # get user_fav_shops
    keys = kvg.keymatch('U\d+_FAVS')
    user_fav_shops = dict([(int(key), set([int(k) for k in kvg.getl(key)])) for key in keys])

    # get blocked shop set
    keys = kvg.keymatch('S\d+_BINFO')
    blocked_shops = set()
    for key in keys:
        if kvg.getk(key, 'block') != '0':
            blocked_shops.add(key_id(key))

    # get user tags by fav shops
    shop_tags

    # get user_shops

    # shop idf

    # weigting and normalizing user_shops

    # 给每个用户做推荐
    print "Recommend for each user, total %d" % len(self.user_shops)
    sys.stdout.flush()
    for no, uid in enumerate(self.user_shops):
        shop_weight = {} # 给该用户推荐的店铺列表及权重
        shops = self.user_shops[uid] # 用户有动作的店铺列表
        fav_shops = self.user_fav_shops.get(uid, {}) # 用户关注的店铺
        if no % 1000 == 0:
            print "%d" % no
            sys.stdout.flush()

        for sid in shops:
            if sid not in self.shop_similarity:
                continue
            simi_shops = self.shop_similarity[sid]
            for ssid in simi_shops:
                if ssid in shop_weight:
                    shop_weight[ssid] += shops[sid] * simi_shops[ssid]
                else:
                    shop_weight[ssid] = shops[sid] * simi_shops[ssid]
        
        # 过滤shop_weight
        shop_weight_new = {}
        for sid in shop_weight:
            # 店铺sid是否适合推荐给用户uid
            if sid in fav_shops:
                continue # 原本就关注
            if sid in self.shop_info and self.shop_info[sid][2] != 0:
                continue # 店铺的block属性非0，被屏蔽，不使用
            if sid in self.shop_tags and uid in self.user_tags and \
                    self._tag_conflict(self.user_tags[uid], self.shop_tags[sid]):
                continue # 用户关注店铺的类型与该店铺不符
            shop_weight_new[sid] = shop_weight[sid]

        if not shop_weight_new:
            continue # 没有为此用户推荐一个店铺，都被过滤掉，不记录

        # 排序，取TOP
        normalize(shop_weight_new)
        items = shop_weight_new.items()
        items.sort(reverse=True, key=lambda x: x[1]) # sort by weight desc

        self.user_recommend_list[uid] = items[:TOP_SHOP_NUM] # limit n

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

