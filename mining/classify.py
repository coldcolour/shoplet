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

def read_rule(fname):
    # cname -> (must have set, optional set)
    rules = {}
    for line in open(fname, 'r'):
        parts = line.strip().split('\t')
        l = len(parts)
        if l <= 2 or l > 3:
            continue
        elif l == 2:
            parts.append('')
        else:
            pass
            
        rules[parts[0]] = (set(parts[1].split(',')), set(parts[2].split(',')))
    return rules

def classify(name, rules):
    score_board = {} # cname -> score
    for cname in rules:
        mset, oset = rules[cname]
        if not mset:
            continue
        exists = [item in name for item in mset]
        if not all(exists):
            continue
        score_board[cname] = 100
        for item in oset:
            if item in name:
                score_board[cname] += len(item)
    items = score_board.items()
    items.sort(key=lambda x:x[1], reverse=True)
    items = items[:3]
    return ['%s:%d' % item for item in items]

def main():
    if len(sys.argv) != 3:
        print 'Usage:<goods.name> <rule>'
        sys.exit(0)

    rules = read_rule(sys.argv[2])
    fgoodsname = open(sys.argv[1])
    for no, line in enumerate(fgoodsname):
        parts = line.strip().split('\t')
        if len(parts) != 2:
            continue
        gid = int(parts[0])
        name = parts[1]
        categories = classify(name, rules)
        for category in categories:
            print '%d\t%s\t%s' % (gid, name, category)
    fgoodsname.close()

if __name__ == '__main__':
    main()
