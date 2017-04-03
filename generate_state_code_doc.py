#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Usage: python generate_state_code_doc.py > docs/state_code.md
"""


from collections import OrderedDict

import jimit as ji
from state_code import *


__author__ = 'James Iter'
__date__ = '16/8/21'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2016 by James Iter.'


ji.index_state['branch'] = dict(ji.index_state['branch'], **own_state_branch)

print '# 状态码'
print '## 干状态码'
print '|CODE|zh-cn|en-us|'
print '|:--:|:--|:--|'
for k, v in OrderedDict(sorted(ji.index_state['trunk'].items(), key=lambda t: t[0])).items():
    print '|' + '|'.join([v['code'], v['zh-cn'], v['en-us']]) + '|'

print ''
print '## 枝状态码'
print '|CODE|zh-cn|'
print '|:--:|:--|'
for k, v in OrderedDict(sorted(ji.index_state['branch'].items(), key=lambda t: t[0])).items():
    print '|' + '|'.join([v['code'], v['zh-cn']]) + '|'

print ''
print '[返回上一级](../README.md)'
print '==='
