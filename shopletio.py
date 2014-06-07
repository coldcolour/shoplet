#!/user/bin/python
#encoding:utf-8
"""
各种文件格式的读写函数库
"""
FN_FOLLOW = "follow.csv"
FN_SHOP = "shop.csv"
FN_SHOP_TAG = "shoptag.csv"

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
            shop_users.setdefault(sid, {})[uid] = 1.0
            user_shops.setdefault(uid, {})[sid] = 1.0
        except ValueError:
            continue
    f.close()

    print "%d user->shop relationship" % len(user_shops)
    print "%d shop->user relationship" % len(shop_users)
    return user_shops, shop_users

def read_shop_info(fn = FN_SHOP):
    # 店铺属性数据: "taobao_shop_id","taobao_shop_domain","taobao_shop_title","taobao_shop_like_num","taobao_type","taobao_block"
    shop_info = {}

    f = open(fn, 'r')
    for no, line in enumerate(f):
        if no == 0:
            continue
        # uid, shopid
        parts = line.strip().split('\t')
        if len(parts) != 6:
            continue
        try:
            sid = int(parts[0].strip('"'))
            domain = parts[1].strip('"')
            title = parts[2].strip('"')
            BorC = parts[4].strip('"')
            if BorC == "B":
                domain = "%s.tmall.com" % domain
            else:
                domain = "%s.taobao.com" % domain
            block = int(parts[5].strip('"'))
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
            shop_tags.setdefault(sid, set()).add(tagid)
        except ValueError:
            continue
    f.close()

    print "%d shop tags read" % len(shop_tags)
    return shop_tags

