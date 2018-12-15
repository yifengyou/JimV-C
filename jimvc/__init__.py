#!/usr/bin/env python
# -*- coding: utf-8 -*-


import traceback
import time
from datetime import timedelta
import jimit as ji
import json

import os
from flask import g, request, redirect, url_for, Response, session, Flask

try:
    from flask_session import Session
except ImportError as e:
    # 兼容老版本
    from flask.ext.session import Session

try:
    from flask_themes2 import Themes, packaged_themes_loader
except ImportError as e:
    # 兼容老版本
    from flask.ext.themes2 import Themes, packaged_themes_loader

from werkzeug.debug import get_current_traceback

app = Flask(__name__)

from jimvc.models.initialize import logger, Init, app_config, dev_table

import api_route_table
import views_route_table

from jimvc.models import Utils
from jimvc.models import EventProcessor
from jimvc.models import Database as db
from jimvc.models import Config
from jimvc.models import User

from jimvc.api.user import blueprint as user_blueprint
from jimvc.api.os_template_image import blueprint as os_template_image_blueprint
from jimvc.api.os_template_image import blueprints as os_template_image_blueprints
from jimvc.api.os_template_initialize_operate_set import blueprint as os_template_initialize_operate_set_blueprint
from jimvc.api.os_template_initialize_operate_set import blueprints as os_template_initialize_operate_set_blueprints
from jimvc.api.os_template_initialize_operate import blueprint as os_template_initialize_operate_blueprint
from jimvc.api.os_template_initialize_operate import blueprints as os_template_initialize_operate_blueprints
from jimvc.api.os_template_profile import blueprint as os_template_profile_blueprint
from jimvc.api.os_template_profile import blueprints as os_template_profile_blueprints
from jimvc.api.guest import blueprint as guest_blueprint
from jimvc.api.guest import blueprints as guest_blueprints
from jimvc.api.disk import blueprint as disk_blueprint
from jimvc.api.disk import blueprints as disk_blueprints
from jimvc.api.config import blueprint as config_blueprint
from jimvc.api.ip_pool import blueprint as ip_pool_blueprint
from jimvc.api.ip_pool import blueprints as ip_pool_blueprints
from jimvc.api.log import blueprint as log_blueprint
from jimvc.api.log import blueprints as log_blueprints
from jimvc.api.host import blueprint as host_blueprint
from jimvc.api.host import blueprints as host_blueprints
from jimvc.api.ssh_key import blueprint as ssh_key_blueprint
from jimvc.api.ssh_key import blueprints as ssh_key_blueprints
from jimvc.api.snapshot import blueprint as snapshot_blueprint
from jimvc.api.snapshot import blueprints as snapshot_blueprints
from jimvc.api.guest_performance import blueprint as performance_blueprint
from jimvc.api.guest_performance import blueprints as performance_blueprints
from jimvc.api.host_performance import blueprint as host_performance_blueprint
from jimvc.api.host_performance import blueprints as host_performance_blueprints
from jimvc.api.dashboard import blueprint as dashboard_blueprint
from jimvc.api.dashboard import blueprints as dashboard_blueprints
from jimvc.api.about import blueprint as about_blueprint
from jimvc.api.project import blueprint as project_blueprint
from jimvc.api.project import blueprints as project_blueprints
from jimvc.api.service import blueprint as service_blueprint
from jimvc.api.service import blueprints as service_blueprints

from jimvc.views.error_pages import *
from jimvc.views.config import blueprint as view_config_blueprint
from jimvc.views.misc import blueprint as view_misc_blueprint
from jimvc.views.dashboard import blueprint as view_dashboard_blueprint
from jimvc.views.guest import blueprint as view_guest_blueprint
from jimvc.views.guest import blueprints as view_guest_blueprints
from jimvc.views.disk import blueprint as view_disk_blueprint
from jimvc.views.disk import blueprints as view_disk_blueprints
from jimvc.views.log import blueprint as view_log_blueprint
from jimvc.views.log import blueprints as view_log_blueprints
from jimvc.views.os_template_image import blueprint as view_os_template_image_blueprint
from jimvc.views.os_template_image import blueprints as view_os_template_image_blueprints
from jimvc.views.ssh_key import blueprint as view_ssh_key_blueprint
from jimvc.views.ssh_key import blueprints as view_ssh_key_blueprints
from jimvc.views.snapshot import blueprint as view_snapshot_blueprint
from jimvc.views.snapshot import blueprints as view_snapshot_blueprints

from jimvc.views.host import blueprint as view_host_blueprint
from jimvc.views.host import blueprints as view_host_blueprints

from websockify.websocketproxy import WebSocketProxy


__author__ = 'James Iter'
__date__ = '2017/3/31'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


app.config = dict(app.config, **app_config)
app.jinja_env.add_extension('jinja2.ext.i18n')
app.jinja_env.add_extension('jinja2.ext.do')
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.jinja_env.auto_reload = app.config['DEBUG']

# 替换为Flask-Session
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=app_config['PERMANENT_SESSION_LIFETIME'])
Session(app)
Themes(app, app_identifier="JimV-C")
themes_list = packaged_themes_loader(app)


def instantiation_ws_vnc(listen_port, target_host, target_port):
    # 用于 Web noVNC 代理
    ws = WebSocketProxy(listen_host="0.0.0.0", listen_port=listen_port, target_host=target_host,
                        target_port=target_port, run_once=True, daemon=True, idle_timeout=10)
    ws.start_server()


def ws_engine_for_vnc():
    logger.info(msg='VNC ws engine is launched.')

    while True:
        payload = db.r.lpop(app_config['ipc_queue'])

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
        'api_user.r_send_reset_password_email',
        '_themes.static'
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
                g.token['exp'] < (ji.Common.ts() + (app_config['token_ttl'] / 2)):
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
    app.register_blueprint(ip_pool_blueprint)
    app.register_blueprint(ip_pool_blueprints)
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
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(dashboard_blueprints)
    app.register_blueprint(about_blueprint)
    app.register_blueprint(project_blueprint)
    app.register_blueprint(project_blueprints)
    app.register_blueprint(service_blueprint)
    app.register_blueprint(service_blueprints)

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

