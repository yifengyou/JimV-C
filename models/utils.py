#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps

from flask import make_response, g, request
from flask.wrappers import Response
from werkzeug.utils import import_string, cached_property
import jwt

from models.initialize import *


__author__ = 'James Iter'
__date__ = '16/06/08'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2016 by James Iter.'


class Utils(object):

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


def add_rule(blueprint, rule, view_func=None, **options):
    blueprint.add_url_rule(rule=rule, view_func=LazyView(''.join(['views.', view_func])), **options)
