#!/usr/local/bin/python
#encoding:utf8
'''
Classify goods by name and rules.

Rule format: cat1/cat2/cat3,aaa&bbb&ccc|ddd&!eee -> all(aaa, bbb) in name, any(ccc, ddd) in name, no(eee) in name
'''
import sys
import os
import re

def read_rule(fname):
    rules = {}
    frule = open(fname, 'r')

    for line in frule:
        parts = line.strip().split(',')
        if len(parts) != 2:
            continue
        category = parts[0]
        subparts = parts[1].split('&')
        rule_res = []
        for sp in subparts:
            if sp.startswith('!'):
                rule_res.append(re.compile("^((?!%s).)*$" % sp[1:], re.DOTALL))
            elif '|' in sp:
                rule_res.append(re.compile("(%s)" % ('|'.join(["(%s)" % ssp for ssp in sp.split('|')])), re.DOTALL))
            else:
                rule_res.append(re.compile("%s" % sp, re.DOTALL))
        rules[category] = rule_res

    frule.close()
    return rules

def classify(name, rules):
    cats = []
    for cat in rules:
        if all([reitem.search(name) for reitem in rules[cat]]):
            cats.append(cat)
    if cats:
        cats.sort()
        new_cats = []
        n = len(cats)
        for i in range(n-1):
            if cats[i] in cats[i+1]:
                continue
            else:
                new_cats.append(cats[i])
        new_cats.append(cats[-1])
        return new_cats
    else:
        return cats

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
        categories = classify(name.lower(), rules) 
        if not categories:
            print '%d\t%s\tNOCAT' % (gid, name)
        else:
            for category in categories:
                print '%d\t%s\t%s' % (gid, name, category)

    fgoodsname.close()

if __name__ == '__main__':
    main()
