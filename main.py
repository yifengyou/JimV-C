#!/usr/bin/env python
# -*- coding: utf-8 -*-


import traceback
import signal

import time
from datetime import timedelta
import jimit as ji
import json

import os
import threading
from flask import g, request, redirect, url_for, Response, session
from flask.ext.session import Session
from werkzeug.debug import get_current_traceback

from models import Utils
from models.event_processor import EventProcessor
from models.initialize import logger, Init
import api_route_table
import views_route_table
from models import Database as db
from models import Config
from models import User
from api.user import blueprint as user_blueprint

from api.os_template_image import blueprint as os_template_image_blueprint
from api.os_template_image import blueprints as os_template_image_blueprints
from api.os_template_initialize_operate_set import blueprint as os_template_initialize_operate_set_blueprint
from api.os_template_initialize_operate_set import blueprints as os_template_initialize_operate_set_blueprints
from api.os_template_initialize_operate import blueprint as os_template_initialize_operate_blueprint
from api.os_template_initialize_operate import blueprints as os_template_initialize_operate_blueprints
from api.os_template_profile import blueprint as os_template_profile_blueprint
from api.os_template_profile import blueprints as os_template_profile_blueprints
from api.guest import blueprint as guest_blueprint
from api.guest import blueprints as guest_blueprints
from api.disk import blueprint as disk_blueprint
from api.disk import blueprints as disk_blueprints
from api.config import blueprint as config_blueprint
from api.log import blueprint as log_blueprint
from api.log import blueprints as log_blueprints
from api.host import blueprint as host_blueprint
from api.host import blueprints as host_blueprints
from api.ssh_key import blueprint as ssh_key_blueprint
from api.ssh_key import blueprints as ssh_key_blueprints
from api.snapshot import blueprint as snapshot_blueprint
from api.snapshot import blueprints as snapshot_blueprints
from api.guest_performance import blueprint as performance_blueprint
from api.guest_performance import blueprints as performance_blueprints
from api.host_performance import blueprint as host_performance_blueprint
from api.host_performance import blueprints as host_performance_blueprints

from views.error_pages import *
from views.config import blueprint as view_config_blueprint
from views.misc import blueprint as view_misc_blueprint
from views.dashboard import blueprint as view_dashboard_blueprint
from views.guest import blueprint as view_guest_blueprint
from views.guest import blueprints as view_guest_blueprints
from views.disk import blueprint as view_disk_blueprint
from views.disk import blueprints as view_disk_blueprints
from views.log import blueprint as view_log_blueprint
from views.log import blueprints as view_log_blueprints
from views.os_template_image import blueprint as view_os_template_image_blueprint
from views.os_template_image import blueprints as view_os_template_image_blueprints
from views.ssh_key import blueprint as view_ssh_key_blueprint
from views.ssh_key import blueprints as view_ssh_key_blueprints
from views.snapshot import blueprint as view_snapshot_blueprint
from views.snapshot import blueprints as view_snapshot_blueprints

from views.host import blueprint as view_host_blueprint
from views.host import blueprints as view_host_blueprints

from websockify.websocketproxy import WebSocketProxy


__author__ = 'James Iter'
__date__ = '2017/3/31'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


# 替换为Flask-Session
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=app.config['PERMANENT_SESSION_LIFETIME'])
Session(app)


def instantiation_ws_vnc(listen_port, target_host, target_port):
    # 用于 Web noVNC 代理
    ws = WebSocketProxy(listen_host="0.0.0.0", listen_port=listen_port, target_host=target_host,
                        target_port=target_port, run_once=True, daemon=True, idle_timeout=10)
    ws.start_server()


def ws_engine_for_vnc():

    logger.info(msg='VNC ws engine is launched.')

    while True:
        payload = db.r.lpop(app.config['ipc_queue'])

        if payload is None:
            time.sleep(1)
            continue

        payload = json.loads(payload)

        c_pid = os.fork()
        if c_pid == 0:
            instantiation_ws_vnc(payload['listen_port'], payload['target_host'], payload['target_port'])

        # 因为 WebSocketProxy 使用了 daemon 参数，所以当执行到 ws.start_server() 时，会退出其所在的子进程，
        # 故而这里设置wait来处理结束的子进程的环境，避免出现僵尸进程。
        os.wait()


def is_not_need_to_auth(endpoint):
    not_auth_table = [
        'api_config.r_get',
        'api_config.r_create',
        'v_config.create',
        'v_misc.login',
        'v_misc.recover_password',
        'v_misc.reset_password',
        'api_user.r_sign_in',
        'api_user.r_reset_password',
        'api_user.r_send_reset_password_email'
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

            token = session.get('token', '')
            g.token = Utils.verify_token(token)

            user = User()
            user.id = g.token['uid']

            try:
                user.get()
            except ji.PreviewingError, e:
                # 如果该用户获取失败，则清除该用户对应的session。因为该用户可能已经被删除。
                for key in session.keys():
                    session.pop(key=key)
                return json.loads(e.message)

    except ji.JITError, e:
        ret = json.loads(e.message)

        if ret['state']['code'] == '404':
            return redirect(location=url_for('v_config.create'), Response=Response)

        if ret['state']['sub']['code'] in ['41208']:
            return redirect(location=url_for('v_misc.login'), Response=Response)

        return ret


@app.after_request
@Utils.dumps2response
def r_after_request(response):
    try:
        # https://developer.mozilla.org/en/HTTP_access_control
        # (中文版) https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Access_control_CORS#Access-Control-Allow-Credentials
        # http://www.w3.org/TR/cors/
        # 由于浏览器同源策略，凡是发送请求url的协议、域名、端口三者之间任意一与当前页面地址不同即为跨域。

        if request.referrer is None:
            # 跑测试脚本时，用该规则。
            response.headers['Access-Control-Allow-Origin'] = '*'
        else:
            # 生产环境中，如果前后端分离。那么请指定具体的前端域名地址，不要用如下在开发环境中的便捷方式。
            # -- Access-Control-Allow-Credentials为true，携带cookie时，不允许Access-Control-Allow-Origin为通配符，是浏览器对用户的一种安全保护。
            # -- 至少能避免登录山寨网站，骗取用户相关信息。
            response.headers['Access-Control-Allow-Origin'] = '/'.join(request.referrer.split('/')[:3])

        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'HEAD, GET, POST, DELETE, OPTIONS, PATCH, PUT'
        response.headers['Access-Control-Allow-Headers'] = 'X-Request-With, Content-Type'
        response.headers['Access-Control-Expose-Headers'] = 'Set-Cookie'

        # 少于session生命周期一半时,自动对其续期
        if not is_not_need_to_auth(request.endpoint) and hasattr(g, 'token') and \
                        g.token['exp'] < (ji.Common.ts() + (app.config['token_ttl'] / 2)):
            token = Utils.generate_token(g.token['uid'])
            # 清除原有session，由新session代替
            for key in session.keys():
                session.pop(key=key)
            session['token'] = token
        return response
    except ji.JITError, e:
        return json.loads(e.message)


@app.teardown_request
def teardown_request(exception):
    if exception:
        _traceback = get_current_traceback()
        logger.error(_traceback.plaintext)


# noinspection PyBroadException
try:
    db.init_conn_mysql()
    db.init_conn_redis()

    app.register_blueprint(user_blueprint)

    app.register_blueprint(os_template_image_blueprint)
    app.register_blueprint(os_template_image_blueprints)
    app.register_blueprint(os_template_initialize_operate_set_blueprint)
    app.register_blueprint(os_template_initialize_operate_set_blueprints)
    app.register_blueprint(os_template_initialize_operate_blueprint)
    app.register_blueprint(os_template_initialize_operate_blueprints)
    app.register_blueprint(os_template_profile_blueprint)
    app.register_blueprint(os_template_profile_blueprints)
    app.register_blueprint(guest_blueprint)
    app.register_blueprint(guest_blueprints)
    app.register_blueprint(disk_blueprint)
    app.register_blueprint(disk_blueprints)
    app.register_blueprint(config_blueprint)
    app.register_blueprint(log_blueprint)
    app.register_blueprint(log_blueprints)
    app.register_blueprint(host_blueprint)
    app.register_blueprint(host_blueprints)
    app.register_blueprint(ssh_key_blueprint)
    app.register_blueprint(ssh_key_blueprints)
    app.register_blueprint(snapshot_blueprint)
    app.register_blueprint(snapshot_blueprints)
    app.register_blueprint(performance_blueprint)
    app.register_blueprint(performance_blueprints)
    app.register_blueprint(host_performance_blueprint)
    app.register_blueprint(host_performance_blueprints)

    app.register_blueprint(view_config_blueprint)
    app.register_blueprint(view_misc_blueprint)
    app.register_blueprint(view_dashboard_blueprint)
    app.register_blueprint(view_guest_blueprint)
    app.register_blueprint(view_guest_blueprints)
    app.register_blueprint(view_disk_blueprint)
    app.register_blueprint(view_disk_blueprints)
    app.register_blueprint(view_log_blueprint)
    app.register_blueprint(view_log_blueprints)
    app.register_blueprint(view_os_template_image_blueprint)
    app.register_blueprint(view_os_template_image_blueprints)
    app.register_blueprint(view_ssh_key_blueprint)
    app.register_blueprint(view_ssh_key_blueprints)
    app.register_blueprint(view_snapshot_blueprint)
    app.register_blueprint(view_snapshot_blueprints)

    app.register_blueprint(view_host_blueprint)
    app.register_blueprint(view_host_blueprints)

except:
    logger.error(traceback.format_exc())

threads = []
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

        t_ = threading.Thread(target=EventProcessor.launch, args=())
        threads.append(t_)

        t_ = threading.Thread(target=Init.pub_sub_ping_pong, args=())
        threads.append(t_)

        t_ = threading.Thread(target=Init.clear_expire_monitor_log, args=())
        threads.append(t_)

        for t in threads:
            t.start()

except:
    logger.error(traceback.format_exc())
    exit(-1)


if __name__ == '__main__':
    # noinspection PyBroadException
    try:

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

