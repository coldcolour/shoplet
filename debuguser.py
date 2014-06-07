#!/usr/bin/python
#encoding:utf8
'''
Debug给一个用户的推荐是如何产生的。

Input: 
    user id

Output: 
    userid.debug.html
    用户ID
    用户关注了哪些店铺，链接
    店铺相关店铺信息，链接、分数
'''
import os
import sys
from shopletio import read_user_shop, read_shop_info, read_shop_tag, read_user_recommend
from cStringIO import StringIO

def get_shop_link(sid, shop_info, shop_tags = None):
    if sid not in shop_info:
        return ""
    elif shop_tags and sid in shop_tags:
        si = shop_info[sid]
        tags = shop_tags[sid] # set of (tagid, tagname)
        return "<a href='http://%s' target='_blank'>%s<small>(%s)</small></a>" % (si[0], si[1], ','.join([item[1] for item in tags]))
    else:
        si = shop_info[sid]
        return "<a href='http://%s' target='_blank'>%s</a>" % (si[0], si[1])

def get_html_header():
    return \
        """
        <html>
            <head><meta http-equiv=Content-Type content="text/html;charset=utf-8">
                <title></title>
                <style> table{border-collapse:collapse} table th,table td{border:1px solid #000; padding:0} </style>
            </head>\r\n
            <body>
        """

def get_html_tail():
    return \
        """
        </body></html>
        """

def main():
    if len(sys.argv) != 2:
        print "Usage: <uid>"
        sys.exit()

    uid = int(sys.argv[1])
    user_shops, shop_users = read_user_shop()
    shop_info = read_shop_info()
    shop_tags = read_shop_tag()
    user_recommend_list = read_user_recommend()

    buf = StringIO()
    buf.write(get_html_header())
    buf.write("<h1>用户ID：%s</h1>\n" % uid)

    # 给用户推荐的店铺
    if uid not in user_recommend_list:
        print "nothing recommended for this user"
        return
    rlist = user_recommend_list[uid]
    buf.write("<h2>给用户推荐的店铺</h2>\n")
    buf.write("<ul>\n")
    for r in rlist:
        buf.write("<li>%s&nbsp;%.2f</li>\n" % (get_shop_link(r, shop_info, shop_tags), rlist[r]))
    buf.write("</ul>\n")

    # 打印用户关注店铺信息
    if uid not in user_shops:
        print "uid not found"
        return
    else:
        buf.write("<h2>用户关注的店铺</h2>\n")
        shops = user_shops[uid].keys()
        buf.write("<ul>\n")
        for sid in shops:
            buf.write("<li>%s</li>\n" % get_shop_link(sid, shop_info, shop_tags))
        buf.write("</ul>\n")

    # 打印店铺相关店铺信息
    buf.write(get_html_tail())
    fout = open("foo.html", 'w')
    fout.write(buf.getvalue())
    fout.close()

if __name__ == "__main__":
    main()
