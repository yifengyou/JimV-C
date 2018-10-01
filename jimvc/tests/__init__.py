#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os


__author__ = 'James Iter'
__date__ = '2017/03/31'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


def load_tests(loader, standard_tests, pattern='test_*.py'):
    # top level directory cached on loader instance
    this_dir = os.path.dirname(__file__)
    package_tests = loader.discover(start_dir=this_dir, pattern=pattern)
    standard_tests.addTests(package_tests)
    return standard_tests
