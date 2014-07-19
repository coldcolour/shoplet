#!/usr/bin/python
#encoding:utf8
import os
import re

RE_DIGITS = re.compile('\d+')

def full_path(fn):
    return os.path.join(os.environ['DATA_DIR'], fn)

def key_id(key):
    kid = int(RE_DIGITS.search(key).group())
    return kid

def write_kv_dict(d, keypat, fn):
    '''
    d: a -> b -> c
    keypat: key pattern, e.g. U%s_ACTS
    fn: file name without path
    '''
    kvpath = full_path(fn)
    fout = open(kvpath, 'w')
    for k in d:
        fout.write('%s\t%s\n' % (keypat % k, ';'.join(['%s:%s' % item for item in d[k].items()])))
    fout.close()

class KVEngine(object):
    def __init__(self):
        self._pool = {}

    def clear(self):
        self._pool.clear()

    def load(self, kv_file_list):
        if not kv_file_list:
            return
        for kvf in kv_file_list:
            fin = open(kvf, 'r')
            for line in fin:
                parts = line.strip().split('\t')
                if len(parts) != 2:
                    continue
                key, value = parts
                self._pool[key] = value
            fin.close()

    def get(self, key):
        return self._pool.get(key, '')

    def __contains__(self, key):
        return key in self._pool

    def getl(self, key):
        '''return a list'''
        value = self.get(key)
        return value.split(';')

    def getd(self, key):
        '''return a dict'''
        value = self.get(key)
        return dict([v.split(':') for v in value.split(';')])

    def getk(self, key, dkey):
        '''return value of value dict'''
        return self.getd.get(dkey, '')

    def keymatch(self, pattern):
        '''return keys that match pattern'''
        return [key for key in self._pool if re.search(pattern, key)]

    def getmatch(self, pattern):
        '''return a dict whose keys all match the pattern'''
        return dict([(key, self._pool[key]) for key in self._pool if re.search(pattern, key)])
