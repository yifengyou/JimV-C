#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import render_template
from models.initialize import app


__author__ = 'James Iter'
__date__ = '2017/9/10'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(error):
    return render_template('500.html'), 500


