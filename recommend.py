#!/user/bin/python
#encoding:utf-8
"""
Input
    follow.csv : 店铺关注关系 "user_id","shop_id"
    shop.csv : 店铺基本信息 "taobao_shop_id","taobao_shop_domain","taobao_shop_title","taobao_shop_like_num"
    shoptag.csv : 店铺分类标签 "taobao_shop_id","shop_tag_id","shop_tag_show_name"

Process:
    基础的item-based协同过滤算法，对用户给出推荐的店铺。
    过滤条件：a) 店铺非block b) 如果用户只关注女装，不出其它分类店铺

Output:
    outcome.csv: table分隔的结果文件，用于装入mysql。uid\t[[sid,weight],[sid,weight],...]
    outcome.html: html文件，以名称链接方式展示推荐结果

"""
import os
import sys
import csv
import math
from cStringIO import StringIO
from shopletio import *

DEBUG = False
TOP_SHOP_NUM = 20
FN_OUT_CSV = "output.csv"
FN_OUT_HTML = "output.html"
RAND_USER_NUM = 100
MAN_CHILD_TAG_SET = set([13, 14, 15, 16])

def normalize(d):
    """
    normalize a dict, key -> value of number
    """
    m = 0.0
    for w in d.values():
        m += w * w
    m = math.sqrt(m)
    if abs(m) >= 1e-5:
        for i in d:
            d[i] /= m

def norm_dot_product(v, w):
    """
    dot product for two dicts, both already normalized
    """
    s = 0.0
    for vv in v:
        if vv in w:
            s += v[vv] * w[vv]
    return s

class Recommender(object):
    def __init__(self):
        self.user_shops = {} # uid -> sid -> weight
        self.shop_users = {} # sid -> uid -> weight
        self.shop_info = {} # sid -> [domain, title]
        self.shop_tags = {} # sid -> tag set
        self.user_tags = {} # uid -> tag set

        self.shop_similarity = {} # sid -> sid -> sim
        self.user_recommend_list = {} # uid -> (sid, weight)[]
        self.shop_idf = {} # sid -> [df, idf]

    def _read_inputs(self):
        self.user_shops, self.shop_users = read_user_shop()
        self.shop_info = read_shop_info()
        self.shop_tags = read_shop_tag()

        # 从店铺tag构造用户tag，用户所有关注的店铺tag就是她的tag集合
        for uid in self.user_shops:
            tag_set = set()
            sids = self.user_shops[uid]
            for sid in sids:
                if sid in self.shop_tags and sid != 1: # 1为默认关注店铺, 排除
                    tag_set.update(self.shop_tags[sid])
            if tag_set:
                self.user_tags[uid] = tag_set
        print "%d user tags constructed" % len(self.user_tags)

        # 计算店铺df，idf, 即每个店铺有几个人关注, idf = log(total_d/(1+df))
        total_d = len(self.user_shops) 
        for sid in self.shop_users:
            df = len(self.shop_users[sid])
            self.shop_idf[sid] = [df, math.log(float(total_d)/(1+df))]

        # 按tf*idf调整用户对店铺关注的权重
        self.shop_users = {} # 使用tf*idf值更新shop users
        for uid in self.user_shops:
            for sid in self.user_shops[uid]:
                if sid in self.shop_idf:
                    self.user_shops[uid][sid] *= self.shop_idf[sid][1]
                    self.shop_users.setdefault(sid, {})[uid] = self.user_shops[uid][sid]

    def _compute_item_relation(self):
        """
        计算店铺两两之间的关系
        """
        # normalization
        for sid in self.shop_users:
            normalize(self.shop_users[sid])

        sids = self.shop_users.keys()
        sids.sort()
        l = len(sids)
        if DEBUG:
            l = 1000
        print "Calculating similarity matrix, total %d..." % l
        for i in range(l):
            if i % 1000 == 0:
                print "%d" % i
                sys.stdout.flush()
            for j in range(i+1, l):
                sim = norm_dot_product(self.shop_users[sids[i]], self.shop_users[sids[j]])
                if abs(sim) < 1e-5:
                    continue
                self.shop_similarity.setdefault(sids[i], {})[sids[j]] = sim
                self.shop_similarity.setdefault(sids[j], {})[sids[i]] = sim

    def _recommend(self):
        """
        产生推荐列表
        """
        # 给每个用户做推荐
        print "Recommend for each user, total %d" % len(self.user_shops)
        sys.stdout.flush()
        for no, uid in enumerate(self.user_shops):
            shop_weight = {} # 给该用户推荐的店铺列表及权重
            shops = self.user_shops[uid] # 用户关注的店铺列表
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
                if sid in shops:
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
    
    def _tag_conflict(self, utags, stags):
        """
        return True if two tag sets conflict each other
        """
        if not utags.intersection(MAN_CHILD_TAG_SET) and not stags.difference(MAN_CHILD_TAG_SET):
            # 如果用户关注的tag中没有男装、童装，而且店铺tag中没有除男装、童装以外的内容
            return True
        else:
            return False

    def _output(self):
        self._stat()
        self._dump_sample_html()
        self._dump_ds()
        self._dump_db()

    def _stat(self):
        # 共推荐多少家不同店铺，推荐出的店铺平均df
        r_shop_set = set()
        r_shop_len = 0
        r_shop_avg_df = 0.0

        for uid in self.user_recommend_list:
            items = self.user_recommend_list[uid]
            r_shop_len += len(items)
            r_shop_set.update([item[0] for item in items])
            r_shop_avg_df += sum([self.shop_idf[item[0]][0] if item[0] in self.shop_idf else 0 for item in items])

        r_shop_avg_df /= r_shop_len
        print "共为%d个用户推荐%d家店铺，平均每个用户推荐%.2f家。不同店铺共%d家，平均推荐出来的店铺被%.2f个用户关注。" \
                % (len(self.user_recommend_list), r_shop_len, float(r_shop_len) / len(self.user_recommend_list), 
                        len(r_shop_set), r_shop_avg_df)

    def _dump_db(self):
        import json
        foutput = open('output.csv', 'w')
        for uid in self.user_recommend_list:
            foutput.write("%d\t%s\n" % (uid, json.dumps(self.user_recommend_list[uid])))
        foutput.close()

    def _dump_ds(self):
        """
        Dump data structures.
        """
        foutput = open("user.shop.dump", "w")
        for uid in self.user_shops:
            foutput.write("%d\t%s\n" % (uid, "\t".join("%d:%.2f" % item for item in self.user_shops[uid].items())))
        foutput.close()

        foutput = open("shop.user.dump", "w")
        for sid in self.shop_users:
            foutput.write("%d\t%s\n" % (sid, "\t".join("%d:%.2f" % item for item in self.shop_users[sid].items())))
        foutput.close()

        foutput = open('shop.info.dump', 'w')
        for sid in self.shop_info:
            foutput.write('%d\t%s\n' % (sid, '\t'.join('%s' % i for i in self.shop_info[sid])))
        foutput.close()

        foutput = open("shop.tags.dump", 'w')
        for sid in self.shop_tags:
            foutput.write("%d\t%s\n" % (sid, '\t'.join("%s" % tag[0] for tag in self.shop_tags[sid])))
        foutput.close()
        
        foutput = open("user.tags.dump", 'w')
        for uid in self.user_tags:
            foutput.write("%d\t%s\n" % (uid, '\t'.join("%s" % tag[0] for tag in self.user_tags[uid])))
        foutput.close()

        foutput = open('shop.sim.dump', 'w')
        for sid in self.shop_similarity:
            foutput.write("%d\t%s\n" % (sid, '\t'.join('%d:%.2f' % item for item in self.shop_similarity[sid].items())))
        foutput.close()

        foutput = open('user.recommend.dump', 'w')
        for uid in self.user_recommend_list:
            foutput.write('%d\t%s\n' % (uid, '\t'.join('%d:%.2f' % item for item in self.user_recommend_list[uid])))
        foutput.close()

    def _dump_sample_html(self):
        buffer = StringIO()
        foutput = open(FN_OUT_HTML, 'w')
        buffer.write(
            """
            <html>
                <head><meta http-equiv=Content-Type content="text/html;charset=utf-8">
                    <title></title>
                    <style> table{border-collapse:collapse} table th,table td{border:1px solid #000; padding:0} </style>
                </head>\r\n
            """)
        buffer.write("<table><tr><td>user id</td><td>用户关注店铺</td><td>推荐店铺</td></tr>")
        uids = self.user_shops.keys()
        import random
        random_uids = random.sample(uids, RAND_USER_NUM)
        for uid in random_uids:
            if uid not in self.user_recommend_list:
                continue # 未能为此用户推荐店铺
            buffer.write("<tr><td>%d</td>" % uid)    
            buffer.write("<td>")
            for item in self.user_shops[uid].items():
                si = self.shop_info.get(item[0], ("block", "block_%d" % item[0]))
                buffer.write("<a href='http://%s' target='_blank'>%s</a></br>" % (si[0], si[1]))
            buffer.write("</td>")
            buffer.write("<td>")
            for item in self.user_recommend_list[uid]:
                si = self.shop_info.get(item[0], ("block", "block_%d" % item[0]))
                buffer.write("<a href='http://%s' target='_blank'>%s</a>:%.2f</br>" % (si[0], si[1], item[1]))
            buffer.write("</td>")
            buffer.write("</tr>\r\n")
        buffer.write("</table>")
        buffer.write("</html>")
        foutput.write(buffer.getvalue())
        foutput.close()

    def run(self):
        self._read_inputs() # read inputs from raw files
        self._compute_item_relation() # compute similarity between shops
        self._recommend() # recommend for each user
        self._output() # output

def main():
    r = Recommender()
    r.run()

if __name__ == "__main__":
    main()
