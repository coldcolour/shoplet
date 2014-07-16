#!/usr/bin/python
#encoding:utf8
import os

def full_path(fn):
    return os.path.join(os.environ['DATA_DIR'], fn)

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

