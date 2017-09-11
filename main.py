#!/usr/bin/env python
# -*- coding: utf-8 -*-


import traceback
import signal

import time
import jimit as ji
import json

import os
import threading
from flask import g, request, redirect, url_for, Response

from models import Utils
from models.event_processor import EventProcessor
from models.initialize import app, logger, q_ws, Init
import api_route_table
import views_route_table
from models import Database as db
from models import Config
from api.boot_job import blueprint as boot_job_blueprint
from api.boot_job import blueprints as boot_job_blueprints
from api.operate_rule import blueprint as operate_rule_blueprint
from api.operate_rule import blueprints as operate_rule_blueprints
from api.os_template import blueprint as os_template_blueprint
from api.os_template import blueprints as os_template_blueprints
from api.guest import blueprint as guest_blueprint
from api.guest import blueprints as guest_blueprints
from api.disk import blueprint as disk_blueprint
from api.disk import blueprints as disk_blueprints
from api.config import blueprint as config_blueprint
from api.log import blueprint as log_blueprint
from api.log import blueprints as log_blueprints
from api.host import blueprint as host_blueprint
from api.host import blueprints as host_blueprints
from api.performance import blueprint as performance_blueprint
from api.performance import blueprints as performance_blueprints
from api.host_performance import blueprint as host_performance_blueprint
from api.host_performance import blueprints as host_performance_blueprints

from views.error_pages import *
from views.config import blueprint as view_config_blueprint
from views.dashboard import blueprint as view_dashboard_blueprint
from views.guest import blueprint as view_guest_blueprint
from views.guest import blueprints as view_guest_blueprints
from views.disk import blueprint as view_disk_blueprint
from views.disk import blueprints as view_disk_blueprints
from views.log import blueprint as view_log_blueprint
from views.log import blueprints as view_log_blueprints
from views.os_template import blueprint as view_os_template_blueprint
from views.os_template import blueprints as view_os_template_blueprints
from views.boot_job import blueprint as view_boot_job_blueprint
from views.boot_job import blueprints as view_boot_job_blueprints
from views.operate_rule import blueprint as view_operate_rule_blueprint
from views.operate_rule import blueprints as view_operate_rule_blueprints
from views.host import blueprint as view_host_blueprint
from views.host import blueprints as view_host_blueprints

from websockify.websocketproxy import WebSocketProxy


__author__ = 'James Iter'
__date__ = '2017/3/31'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


def instantiation_ws_vnc(listen_port, target_host, target_port):
    # 用于 Web noVNC 代理
    ws = WebSocketProxy(listen_host="0.0.0.0", listen_port=listen_port, target_host=target_host,
                        target_port=target_port, run_once=True, daemon=True, idle_timeout=10)
    ws.start_server()


def ws_engine_for_vnc():
    while True:
        payload = q_ws.get()
        payload = json.loads(payload)

        c_pid = os.fork()
        if c_pid == 0:
            instantiation_ws_vnc(payload['listen_port'], payload['target_host'], payload['target_port'])

        # 因为 WebSocketProxy 使用了 daemon 参数，所以当执行到 ws.start_server() 时，会退出其所在的子进程，
        # 故而这里设置wait来处理结束的子进程的环境，避免出现僵尸进程。
        os.wait()
        q_ws.task_done()


def is_not_need_to_auth(endpoint):
    not_auth_table = [
        'api_config.r_get',
        'api_config.r_create',
        'v_config.create'
    ]

    if endpoint in not_auth_table:
        return True

    return False


@app.before_request
@Utils.dumps2response
def r_before_request():
    try:
        g.ts = ji.Common.ts()
        if not is_not_need_to_auth(request.endpoint) and request.blueprint is not None and request.method != 'OPTIONS':
            g.config = Config()
            g.config.id = 1
            g.config.get()

    except ji.JITError, e:
        ret = json.loads(e.message)

        if ret['state']['code'] == '404':
            return redirect(location=url_for('v_config.create'), Response=Response)

        return ret


# noinspection PyBroadException
try:
    db.init_conn_mysql()
    db.init_conn_redis()

    app.register_blueprint(boot_job_blueprint)
    app.register_blueprint(boot_job_blueprints)
    app.register_blueprint(operate_rule_blueprint)
    app.register_blueprint(operate_rule_blueprints)
    app.register_blueprint(os_template_blueprint)
    app.register_blueprint(os_template_blueprints)
    app.register_blueprint(guest_blueprint)
    app.register_blueprint(guest_blueprints)
    app.register_blueprint(disk_blueprint)
    app.register_blueprint(disk_blueprints)
    app.register_blueprint(config_blueprint)
    app.register_blueprint(log_blueprint)
    app.register_blueprint(log_blueprints)
    app.register_blueprint(host_blueprint)
    app.register_blueprint(host_blueprints)
    app.register_blueprint(performance_blueprint)
    app.register_blueprint(performance_blueprints)
    app.register_blueprint(host_performance_blueprint)
    app.register_blueprint(host_performance_blueprints)

    app.register_blueprint(view_config_blueprint)
    app.register_blueprint(view_dashboard_blueprint)
    app.register_blueprint(view_guest_blueprint)
    app.register_blueprint(view_guest_blueprints)
    app.register_blueprint(view_disk_blueprint)
    app.register_blueprint(view_disk_blueprints)
    app.register_blueprint(view_log_blueprint)
    app.register_blueprint(view_log_blueprints)
    app.register_blueprint(view_os_template_blueprint)
    app.register_blueprint(view_os_template_blueprints)
    app.register_blueprint(view_boot_job_blueprint)
    app.register_blueprint(view_boot_job_blueprints)
    app.register_blueprint(view_operate_rule_blueprint)
    app.register_blueprint(view_operate_rule_blueprints)
    app.register_blueprint(view_host_blueprint)
    app.register_blueprint(view_host_blueprints)

except:
    logger.error(traceback.format_exc())

if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        signal.signal(signal.SIGTERM, Utils.signal_handle)
        signal.signal(signal.SIGINT, Utils.signal_handle)

        pid = os.fork()
        if pid == 0:
            ws_engine_for_vnc()

        else:
            # 父进程退出时，会清理所有提前退出的子进程的环境。所以这里无需对子进程做等待操作。
            # 即：即使子进程提前退出，且因父进程没有做wait处理，使其变成了僵尸进程。但当父进程退出时，会对因其所产生的僵尸进程做统一清理操作。

            threads = []
            t_ = threading.Thread(target=EventProcessor.launch, args=())
            threads.append(t_)

            t_ = threading.Thread(target=Init.pub_sub_ping_pong, args=())
            threads.append(t_)

            for t in threads:
                t.start()

            app.run(host=app.config['listen'], port=app.config['port'], use_reloader=False, threaded=True)

            while True:
                if Utils.exit_flag:
                    # 主线程即将结束
                    break
                time.sleep(1)

            # 等待子线程结束
            for t in threads:
                t.join()

            print 'Main say bye-bye!'

    except:
        logger.error(traceback.format_exc())
        exit(-1)

