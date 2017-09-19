#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import g


__author__ = 'James Iter'
__date__ = '2017/9/19'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class Host(object):

    def __init__(self):
        pass

    @staticmethod
    def alive_check(v):
        """
        JimV-C 2 秒更新一次宿主机信息，这里以 5 秒内没收到更新，作为判断宿主机是否在线的标准
        """

        if 'timestamp' not in v:
            return v

        v['alive'] = False
        if v['timestamp'] + 5 >= g.ts:
            v['alive'] = True

        return v

