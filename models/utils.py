#!/usr/bin/env python
# -*- coding: utf-8 -*-


from functools import wraps

import commands

import time
from flask import make_response, g, request
from flask.wrappers import Response
from werkzeug.utils import import_string, cached_property
import jwt

from models.initialize import *


__author__ = 'James Iter'
__date__ = '2017/03/01'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class Utils(object):

    exit_flag = False
    thread_counter = 0

    @staticmethod
    def shell_cmd(cmd):
        try:
            exit_status, output = commands.getstatusoutput(cmd)

            return exit_status, str(output)

        except Exception as e:
            return -1, e.message

    @classmethod
    def signal_handle(cls, signum=0, frame=None):
        cls.exit_flag = True

    @staticmethod
    def dumps2response(func):
        """
        视图装饰器
        http://dormousehole.readthedocs.org/en/latest/patterns/viewdecorators.html
        """
        @wraps(func)
        def _dumps2response(*args, **kwargs):
            ret = func(*args, **kwargs)

            if func.func_name != 'r_before_request' and ret is None:
                ret = dict()
                ret['state'] = ji.Common.exchange_state(20000)

            if isinstance(ret, dict) and 'state' in ret:
                response = make_response()
                response.data = json.dumps(ret, ensure_ascii=False)
                response.status_code = int(ret['state']['code'])
                if 'redirect' in ret and request.args.get('auto_redirect', 'True') == 'True':
                    response.status_code = int(ret['redirect'].get('code', ret['state']['code']))
                    response.headers['location'] = ret['redirect'].get('location', request.host_url)
                    # 参考链接:
                    # http://werkzeug.pocoo.org/docs/0.11/wrappers/#werkzeug.wrappers.BaseResponse.autocorrect_location_header
                    # 变量操纵位置 werkzeug/wrappers.py
                    response.autocorrect_location_header = False
                return response

            if isinstance(ret, Response):
                return ret

        return _dumps2response

    @staticmethod
    def superuser(func):
        @wraps(func)
        def _superuser(*args, **kwargs):
            if not g.superuser:
                ret = dict()
                ret['state'] = ji.Common.exchange_state(40301)
                return ret

            return func(*args, **kwargs)

        return _superuser

    @staticmethod
    def generate_token(uid):
        payload = {
            'iat': ji.Common.ts(),                                                  # 创建于
            'nbf': ji.Common.ts(),                                                  # 在此之前不可用
            'exp': ji.Common.ts() + app.config['token_ttl'],                        # 过期时间
            'uid': uid
        }
        return jwt.encode(payload=payload, key=app.config['jwt_secret'], algorithm=app.config['jwt_algorithm'])

    @staticmethod
    def verify_token(token):
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        try:
            payload = jwt.decode(jwt=token, key=app.config['jwt_secret'], algorithms=app.config['jwt_algorithm'])
            return payload
        except jwt.InvalidTokenError, e:
            logger.error(e.message)
        ret['state'] = ji.Common.exchange_state(41208)
        raise ji.JITError(json.dumps(ret))


class LazyView(object):
    """
    惰性载入视图
    http://dormousehole.readthedocs.org/en/latest/patterns/lazyloading.html
    """

    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)


def add_rule_api(blueprint, rule, api_func=None, **options):
    blueprint.add_url_rule(rule=rule, view_func=LazyView(''.join(['api.', api_func])), **options)


def add_rule_views(blueprint, rule, views_func=None, **options):
    blueprint.add_url_rule(rule=rule, view_func=LazyView(''.join(['views.', views_func])), **options)


@app.context_processor
def utility_processor():

    def format_price(amount, currency=u'￥'):
        return u'{0:.2f}{1}'.format(amount, currency)

    def format_datetime_by_tus(tus, fmt='%y-%m-%d %H:%M'):
        return time.strftime(fmt, time.localtime(tus/1000/1000))

    def format_guest_status(status):
        from status import GuestState

        color = 'FF645B'
        icon = 'glyph-icon icon-bolt'
        desc = '未知状态'

        if status == GuestState.running.value:
            color = '00BB00'
            icon = 'glyph-icon icon-circle'
            desc = '运行中'

        elif status == GuestState.no_state.value:
            color = 'FFC543'
            icon = 'glyph-icon icon-spinner'
            desc = '创建中'

        elif status == GuestState.blocked.value:
            color = '3D4245'
            icon = 'glyph-icon icon-minus-square'
            desc = '被阻塞'

        elif status == GuestState.paused.value:
            color = 'B7B904'
            icon = 'glyph-icon icon-pause'
            desc = '暂停'

        elif status == GuestState.shutdown.value:
            color = '4E5356'
            icon = 'glyph-icon icon-terminal'
            desc = '关闭'

        elif status == GuestState.shutoff.value:
            color = 'FFC543'
            icon = 'glyph-icon icon-plug'
            desc = '断电'

        elif status == GuestState.crashed.value:
            color = '9E2927'
            icon = 'glyph-icon icon-question'
            desc = '已崩溃'

        elif status == GuestState.pm_suspended.value:
            color = 'FCFF07'
            icon = 'glyph-icon icon-anchor'
            desc = '悬挂'

        elif status == GuestState.migrating.value:
            color = '1CF5E7'
            icon = 'glyph-icon icon-space-shuttle'
            desc = '迁移中'

        elif status == GuestState.dirty.value:
            color = 'FF0707'
            icon = 'glyph-icon icon-remove'
            desc = '创建失败，待清理'

        else:
            pass

        return '<span class="{icon}" style="color: #{color};">&nbsp;&nbsp;{desc}</span>'.format(
            icon=icon, color=color, desc=desc)

    return dict(format_price=format_price, format_datetime_by_tus=format_datetime_by_tus,
                format_guest_status=format_guest_status)

