#!/usr/bin/env python
# -*- coding: utf-8 -*-


from functools import wraps
import socket
import subprocess
import jimit as ji
import json
import time

from flask import make_response, g, request
from flask.wrappers import Response
from werkzeug.utils import import_string, cached_property
import jwt

from jimvc.models import app_config, logger, dev_table
from .database import Database as db

from jimvc import app


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
            exit_status, output = subprocess.getstatusoutput(cmd)

            return exit_status, str(output)

        except Exception as e:
            return -1, e.message

    @classmethod
    def signal_handle(cls, signum=0, frame=None):
        cls.exit_flag = True
        raise RuntimeError('Shutdown app!')

    @staticmethod
    def dumps2response(func):
        """
        视图装饰器
        http://dormousehole.readthedocs.org/en/latest/patterns/viewdecorators.html
        """
        @wraps(func)
        def _dumps2response(*args, **kwargs):
            ret = func(*args, **kwargs)

            if func.__name__ != 'r_before_request' and ret is None:
                ret = dict()
                ret['state'] = ji.Common.exchange_state(20000)

            if isinstance(ret, dict) and 'state' in ret:
                response = make_response()
                response.set_data(json.dumps(ret, ensure_ascii=False))
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
    def generate_token(uid, ttl=app_config['token_ttl'], audience=None):
        payload = {
            'iat': ji.Common.ts(),                                                  # 创建于
            'nbf': ji.Common.ts(),                                                  # 在此之前不可用
            'exp': ji.Common.ts() + ttl,                        # 过期时间
            'uid': uid
        }

        if audience is not None:
            payload['aud'] = audience

        return jwt.encode(payload=payload, key=app_config['jwt_secret'], algorithm=app_config['jwt_algorithm'])

    @staticmethod
    def verify_token(token, audience=None):
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        try:
            if audience is None:
                payload = jwt.decode(jwt=token, key=app_config['jwt_secret'], algorithms=app_config['jwt_algorithm'])
            else:
                payload = jwt.decode(jwt=token, key=app_config['jwt_secret'], algorithms=app_config['jwt_algorithm'],
                                     audience=audience)

            return payload
        except jwt.InvalidTokenError as e:
            logger.error(e)
        ret['state'] = ji.Common.exchange_state(41208)
        raise ji.JITError(json.dumps(ret))

    @staticmethod
    def emit_instruction(message):
        db.r.publish(app_config['instruction_channel'], message=message)

    @staticmethod
    def port_is_opened(port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex(('0.0.0.0', port))
        if result == 0:
            return True
        else:
            return False


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
    blueprint.add_url_rule(rule=rule, view_func=LazyView(''.join(['jimvc.api.', api_func])), **options)


def add_rule_views(blueprint, rule, views_func=None, **options):
    blueprint.add_url_rule(rule=rule, view_func=LazyView(''.join(['jimvc.views.', views_func])), **options)


@app.context_processor
def utility_processor():
    def format_price(amount, currency='￥'):
        return '{0:.2f}{1}'.format(amount, currency)

    def format_datetime_by_ts(ts, fmt='%Y-%m-%d %H:%M'):
        return time.strftime(fmt, time.localtime(ts))

    def format_datetime_by_tus(tus, fmt='%y-%m-%d %H:%M'):
        return time.strftime(fmt, time.localtime(tus / 1000 / 1000))

    def format_guest_status(_status, progress):
        from jimvc.models import GuestState

        color = 'FF645B'
        icon = 'glyph-icon icon-bolt'
        desc = '未知状态'

        if _status == GuestState.booting.value:
            color = '00BBBB'
            icon = 'glyph-icon icon-circle'
            desc = '启动中'

        elif _status == GuestState.running.value:
            color = '00BB00'
            icon = 'glyph-icon icon-circle'
            desc = '运行中'

        elif _status == GuestState.creating.value:
            color = 'FFC543'
            icon = 'glyph-icon icon-spinner'
            desc = ' '.join(['创建中', str(progress) + '%'])

        elif _status == GuestState.blocked.value:
            color = '3D4245'
            icon = 'glyph-icon icon-minus-square'
            desc = '被阻塞'

        elif _status == GuestState.paused.value:
            color = 'B7B904'
            icon = 'glyph-icon icon-pause'
            desc = '暂停'

        elif _status == GuestState.shutdown.value:
            color = '4E5356'
            icon = 'glyph-icon icon-terminal'
            desc = '关闭'

        elif _status == GuestState.shutoff.value:
            color = 'FFC543'
            icon = 'glyph-icon icon-plug'
            desc = '断电'

        elif _status == GuestState.crashed.value:
            color = '9E2927'
            icon = 'glyph-icon icon-question'
            desc = '已崩溃'

        elif _status == GuestState.pm_suspended.value:
            color = 'FCFF07'
            icon = 'glyph-icon icon-anchor'
            desc = '悬挂'

        elif _status == GuestState.migrating.value:
            color = '1CF5E7'
            icon = 'glyph-icon icon-space-shuttle'
            desc = '迁移中'

        elif _status == GuestState.dirty.value:
            color = 'FF0707'
            icon = 'glyph-icon icon-remove'
            desc = '创建失败，待清理'

        else:
            pass

        return '<span class="{icon}" style="color: #{color};">&nbsp;&nbsp;{desc}</span>'.format(
            icon=icon, color=color, desc=desc)

    def format_sequence_to_device_name(sequence):
        # sequence 不能大于 25。dev_table 序数从 0 开始。
        if sequence == -1:
            return '无'

        if sequence >= dev_table.__len__():
            return 'Unknown'

        return dev_table[sequence]

    def format_disk_state(state):
        from jimvc.models import DiskState

        color = 'FF645B'
        icon = 'glyph-icon icon-bolt'
        desc = '未知状态'

        if state == DiskState.pending.value:
            color = 'FFC543'
            icon = 'glyph-icon icon-spinner'
            desc = '创建中'

        elif state == DiskState.idle.value:
            color = '0077BB'
            icon = 'glyph-icon icon-unlink'
            desc = '待挂载'

        elif state == DiskState.mounted.value:
            color = '00BB00'
            icon = 'glyph-icon icon-link'
            desc = '使用中'

        elif state == DiskState.mounting.value:
            color = '00BBBB'
            icon = 'glyph-icon icon-elusive-upload'
            desc = '挂载中'

        elif state == DiskState.unloading.value:
            color = '93969B'
            icon = 'glyph-icon icon-elusive-download'
            desc = '卸载中'

        elif state == DiskState.dirty.value:
            color = 'FF0707'
            icon = 'glyph-icon icon-remove'
            desc = '创建失败，待清理'

        else:
            pass

        return '<span class="{icon}" style="color: #{color};">&nbsp;&nbsp;{desc}</span>'.format(
            icon=icon, color=color, desc=desc)

    return dict(format_price=format_price, format_datetime_by_tus=format_datetime_by_tus,
                format_datetime_by_ts=format_datetime_by_ts, format_guest_status=format_guest_status,
                format_sequence_to_device_name=format_sequence_to_device_name, format_disk_state=format_disk_state)
