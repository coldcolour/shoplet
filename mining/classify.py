#!/usr/local/bin/python
#encoding:utf8
'''
Classify goods by name and rules.
Name: ../data/goods_name.kv
Rules: ../data/catwords.tsv

In catwords.tsv,
   group name \t must have words \t optional words
'''
import sys
import os

man_woman_child_rule = {
        'man':set('男 商务 绅士 新郎'.split()),
        'woman':set('女 妇 软妹 淑女 雪纺 文胸 裙 OL 通勤 优雅 甜美 性感 露肩 小香风 公主 妈妈 孕妇 包臀 蕾丝 波西米亚 旗袍 打底裤 显瘦 旗袍'.split()),
        'child':set('童 婴儿 宝贝 宝宝 爬服'.split())
        }

def read_rule(fname):
    # cname -> (must have set, optional set)
    rules = {'man':{}, 'woman':{}, 'child':{}}
    for line in open(fname, 'r'):
        parts = line.strip().split('\t')
        l = len(parts)
        if l != 2 and l != 3:
            continue
        elif l == 2:
            parts.append('')
        else:
            pass
            
        if parts[0].startswith('男'):
            rules['man'][parts[0]] = (set(parts[1].split(',')), set(parts[2].split(',')))
        elif parts[0].startswith('女'):
            rules['woman'][parts[0]] = (set(parts[1].split(',')), set(parts[2].split(',')))
        elif parts[0].startswith('童'):
            rules['child'][parts[0]] = (set(parts[1].split(',')), set(parts[2].split(',')))
        else:
            pass

    return rules

def first_level(name):
    global man_woman_child_rule
    first_categories = []

    for first_category in man_woman_child_rule:
        words = man_woman_child_rule[first_category]
        for word in words:
            if word in name:
                first_categories.append(first_category)
                break

    return first_categories

def word_in_name(word, name):
    if '|' not in word:
        return word in name
    else:
        return any([w in name for w in word.split('|')])

def classify(name, rules):
    first_categories = first_level(name) # in []

    if not first_categories:
        return {}
    else:
        score_board = {} # cname -> score
        for first_category in first_categories:
            crules = rules[first_category]
            for cname in crules:
                mset, oset = crules[cname]
                if not mset:
                    continue
                exists = [word_in_name(item, name) for item in mset]
                if not all(exists):
                    continue
                score_board[cname] = 100
                for item in oset:
                    if item in name:
                        score_board[cname] += len(item)

    items = score_board.items()
    items.sort(key=lambda x:x[1], reverse=True)
    items = items[:3]
    return dict(items)

def main():
    if len(sys.argv) != 3:
        print 'Usage:<goods.name> <rule>'
        sys.exit(0)

    rules = read_rule(sys.argv[2])
    fgoodsname = open(sys.argv[1])

    for no, line in enumerate(fgoodsname):
        parts = line.strip().split('\t')
        if len(parts) < 2:
            continue
        gid = int(parts[0])
        name = parts[1]
        categories = classify(name, rules) # in {}, classname -> weight
        if not categories:
            print '%d\t%s\tNOCAT' % (gid, name)
        else:
            for category in categories:
                print '%d\t%s\t%s\t%.2f' % (gid, name, category, categories[category])

    fgoodsname.close()

if __name__ == '__main__':
    main()
