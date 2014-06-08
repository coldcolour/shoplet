#!/user/bin/python
#encoding:utf-8
"""
各种文件格式的读写函数库
"""
FN_FOLLOW = "follow.csv"
FN_SHOP = "shop.csv"
FN_SHOP_TAG = "shoptag.csv"
FN_USER_RECOMMEND = "user.recommend.dump"
FN_SHOP_SIM = "shop.sim.dump"

def read_user_shop(fn = FN_FOLLOW):
    # 用户关注店铺数据: "user_id","shop_id" 
    shop_users = {}
    user_shops = {}

    f = open(fn, 'r')
    for no, line in enumerate(f):
        if no == 0:
            continue
        # uid, shopid
        parts = line.strip().split('\t')
        if len(parts) != 2:
            continue
        try:
            uid = int(parts[0].strip('"'))
            sid = int(parts[1].strip('"'))
            #shop_users.setdefault(sid, {})[uid] = 1.0
            user_shops.setdefault(uid, {})[sid] = 1.0
        except ValueError:
            continue
    f.close()

    # 过滤掉关注店铺超过50的用户
    uid_to_remove = []
    for uid in user_shops:
        if len(user_shops[uid]) >= 50:
            uid_to_remove.append(uid)
    for uid in uid_to_remove:
        user_shops.pop(uid)
    for uid in user_shops:
        for sid in user_shops[uid]:
            shop_users.setdefault(sid, {})[uid] = 1.0

    print "%d user->shop relationship" % len(user_shops)
    print "%d shop->user relationship" % len(shop_users)
    return user_shops, shop_users

def read_shop_info(fn = FN_SHOP):
    # 店铺属性数据: "taobao_shop_id","taobao_shop_domain","taobao_shop_title","taobao_shop_like_num","taobao_type","taobao_block"
    # domain, title, block
    shop_info = {}

    f = open(fn, 'r')
    for no, line in enumerate(f):
        if no == 0:
            continue
        # uid, shopid
        parts = line.strip().split('\t')
        if len(parts) != 7:
            continue
        try:
            sid = int(parts[0].strip('"'))
            domain = parts[1].strip('"')
            title = parts[2].strip('"')
            BorC = parts[4].strip('"')
            block = int(parts[5].strip('"'))
            #if BorC == "B":
            #    domain = "%s.tmall.com" % domain
            #else:
            #    domain = "%s.taobao.com" % domain
            tsid = int(parts[6].strip('"'))
            domain = "shop%d.taobao.com" % tsid
            shop_info[sid] = [domain, title, block]
        except ValueError:
            continue
    f.close()

    print "%d shop info read" % len(shop_info)
    return shop_info

def read_shop_tag(fn = FN_SHOP_TAG):
    # 店铺tag分类: "taobao_shop_id","shop_tag_id","shop_tag_show_name"
    shop_tags = {}

    f = open(fn, 'r')
    for no, line in enumerate(f):
        if no == 0:
            continue
        # uid, shopid
        parts = line.strip().split('\t')
        if len(parts) != 3:
            continue
        try:
            sid = int(parts[0].strip('"'))
            tagid  = int(parts[1].strip('"'))
            tagname = parts[2].strip('"')
            shop_tags.setdefault(sid, set()).add((tagid, tagname))
        except ValueError:
            continue
    f.close()

    print "%d shop tags read" % len(shop_tags)
    return shop_tags

def parse_loose_matrix_line(s):
    """
    Parse line format like: rowid\tcolid:weight\tcolid:weigth.....
    """
    s = s.strip()
    parts = s.split('\t')
    rowid = -1
    columns = {} 
    if len(parts) >= 1:
        try:
            rowid = int(parts[0])
        except ValueError:
            pass
    if len(parts) >= 2:
        for part in parts[1:]:
            subparts = part.split(':')
            if len(subparts) != 2:
                continue
            else:
                try:
                    colid = int(subparts[0])
                    val = float(subparts[1])
                    columns[colid] = val
                except ValueError:
                    pass
    return rowid, columns

def read_user_recommend(fn = FN_USER_RECOMMEND):
    # 用户推荐数据：uid\tsid:weight\tsid:weight
    user_recommend_list = {}

    f = open(fn, 'r')
    for line in f:
        rowid, cols = parse_loose_matrix_line(line)
        if rowid != -1:
            items = cols.items()
            items.sort(reverse=True, key=lambda x:x[1])
            items = items[:20]
            user_recommend_list[rowid] = items
    f.close()

    print "%d user recommend list read" % len(user_recommend_list)
    return user_recommend_list

def read_shop_sim(fn = FN_SHOP_SIM):
    shop_sim = {}

    f = open(fn, 'r')
    for line in f:
        rowid, cols = parse_loose_matrix_line(line)
        if rowid != -1:
            items = cols.items()
            items.sort(reverse=True, key=lambda x:x[1])
            items = items[:20]
            shop_sim[rowid] = items
    f.close()

    print "%d shop sim read" % len(shop_sim)
    return shop_sim

if __name__ == "__main__":
    #read_user_recommend()
    read_user_shop()
    pass
