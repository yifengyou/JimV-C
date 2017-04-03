#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'James Iter'
__date__ = '2017/3/21'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class JimVCException(Exception):
    pass


class PathExist(JimVCException):
    pass


class PathNotExist(JimVCException):
    pass

