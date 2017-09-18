#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint, render_template


__author__ = 'James Iter'
__date__ = '2017/9/12'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'v_misc',
    __name__,
    url_prefix='/'
)


def login():
    return render_template('login.html')


def change_password():
    return render_template('change_password.html')

