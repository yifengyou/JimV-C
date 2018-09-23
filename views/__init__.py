#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask_themes2 import render_theme_template


__author__ = 'James Iter'
__date__ = '2017/5/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


def render(template, **context):
    return render_theme_template('default', template, **context)

