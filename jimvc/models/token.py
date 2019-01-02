#!/usr/bin/env python
# -*- coding: utf-8 -*-


import jimit as ji

from jimvc.models import Database as db


__author__ = 'James Iter'
__date__ = '2019-01-01'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2019 by James Iter.'


class Token(object):

    def __init__(self):
        self.token = None
        self.ttl = 86400

    def generator(self):
        self.token = ji.Common.generate_random_code(length=32)

    def create(self):
        key = 'Z:Token'
        score = ji.Common.ts() + self.ttl
        value = self.token

        # 可重入，不会产生副作用
        # http://redisdoc.com/sorted_set/zadd.html
        db.r.zadd(key, score, value)

    @staticmethod
    def get_all():
        return db.r.zrange('Z:Token', start=0, end=-1, withscores=True, desc=True, score_cast_func=int)

    def valid(self):
        score = db.r.zscore('Z:Token', self.token)

        if score is not None and score >= ji.Common.ts():
            return True

        return False

    def delete(self):
        return db.r.zrem('Z:Token', self.token)

