#!/user/bin/python
#encoding:utf-8
'''
* cfss, user_favs -> 给每个用户推荐，产生cfus.kv，uid\tsid:weight;
* user_favs -> 每个用户的相似用户，cfuu.kv, uid\tuid:weight
'''
from common.kvengine import KVEngine, full_path

def compute_cfuu():
    pass

def compute_cfss():
    # shop_favu -> shop-shop关系矩阵，并保存cfss.kv，shop\tshop:weight;
    kvg = KVEngine()
    print full_path('shop_favu.kv')
    kvg.load([full_path('shop_favu.kv')])
    #import pdb;pdb.set_trace()

def compute_cfus():
    pass

def main():
    compute_cfss()
    compute_cfus()
    compute_cfuu()

if __name__ == '__main__':
    main()

