#!/usr/local/bin/python
#encoding:utf8
'''
Classify goods by name and rules.

Rule format: cat1/cat2/cat3,aaa&bbb&ccc|ddd&!eee -> all(aaa, bbb) in name, any(ccc, ddd) in name, no(eee) in name
'''
import sys
import os

def read_rule(fname):
    rules = {}
    frule = open(fname, 'r')

    for line in frule:
        parts = line.strip().split(',')
        if len(parts) != 2:
            continue
        category = parts[0]
        subparts = parts[1].split('&')
        all_rule = []
        any_rule = []
        no_rule = []
        for sp in subparts:
            if sp.startswith('!'):
                no_rule.append(sp[1:])
            elif '|' in sp:
                any_rule.extend(sp.split('|'))
            else:
                all_rule.append(sp)
        rules[category] = (all_rule, any_rule, no_rule)

    frule.close()
    return rules

def classify(name, rules):
    cats = []
    for cat in rules:
        all_rule, any_rule, no_rule = rules[cat]
        if all([
                not all_rule or all([word in name for word in all_rule]), 
                not any_rule or any([word in name for word in any_rule]), 
                not no_rule or not any([word in name for word in no_rule])
            ]):
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
        categories = classify(name, rules) 
        if not categories:
            print '%d\t%s\tNOCAT' % (gid, name)
        else:
            for category in categories:
                print '%d\t%s\t%s' % (gid, name, category)

    fgoodsname.close()

if __name__ == '__main__':
    main()
