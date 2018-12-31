#!/usr/bin/env python
# -*- coding: utf-8 -*-


import jimit as ji
import json
from flask import Blueprint, request

from jimvc.models import Config
from jimvc.models import app_config
from jimvc.models import Rules
from jimvc.models import Token
from jimvc.models import Utils
from jimvc.models import Host


__author__ = 'James Iter'
__date__ = '2018-12-29'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'api_misc',
    __name__,
    url_prefix='/api/misc'
)

blueprints = Blueprint(
    'api_miscs',
    __name__,
    url_prefix='/api/miscs'
)


@Utils.dumps2response
def r_join(node_id, _token):
    # 如果该 node_id 已经被加入，那么要用户先去计算节点处删除作废的节点后，再添加。
    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)
    ret['data'] = dict()

    args_rules = [
        Rules.NODE_ID.value,
        Rules.TOKEN.value
    ]

    try:
        ji.Check.previewing(args_rules, {'node_id': node_id, 'token': _token})

        token = Token()
        token.token = token

        # 检验 token 有效性
        if not token.valid():
            ret['state'] = ji.Common.exchange_state(41208)
            return ret

        nodes_id = list()
        hosts = Host.get_all()

        for host in hosts:
            nodes_id.append(host['node_id'])

        # 检测 node_id 是否已经存在
        if node_id in nodes_id:
            ret['state'] = ji.Common.exchange_state(40901)

        else:
            config = Config()
            config.id = 1
            config.get()

            ret['data']['redis_host'] = request.host
            ret['data']['redis_port'] = app_config.get('redis_port', 6379)
            ret['data']['redis_password'] = app_config.get('redis_password', '')
            ret['data']['redis_dbid'] = app_config.get('redis_dbid', 0)
            ret['data']['vm_network'] = config.vm_network
            ret['data']['vm_manage_network'] = config.vm_manage_network

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)

