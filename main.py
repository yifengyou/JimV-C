#!/usr/bin/env python
# -*- coding: utf-8 -*-


import traceback
import thread

import signal

import time
import jimit as ji
import json

from flask import g

from models import Utils
from models.event_processor import EventProcessor
from models.initialize import app, logger
import api_route_table
from models import Database as db
from api.os_init import blueprint as os_init_blueprint
from api.os_init import blueprints as os_init_blueprints
from api.os_init_write import blueprint as os_init_write_blueprint
from api.os_init_write import blueprints as os_init_write_blueprints
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


__author__ = 'James Iter'
__date__ = '2017/3/31'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


@app.before_request
@Utils.dumps2response
def r_before_request():
    try:
        g.ts = ji.Common.ts()

    except ji.JITError, e:
        ret = json.loads(e.message)
        return ret


# noinspection PyBroadException
try:
    db.init_conn_mysql()
    thread.start_new_thread(db.keepalived_mysql, ())
    db.init_conn_redis()

    app.register_blueprint(os_init_blueprint)
    app.register_blueprint(os_init_blueprints)
    app.register_blueprint(os_init_write_blueprint)
    app.register_blueprint(os_init_write_blueprints)
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

except:
    logger.error(traceback.format_exc())

if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        signal.signal(signal.SIGTERM, Utils.signal_handle)
        signal.signal(signal.SIGINT, Utils.signal_handle)

        thread.start_new_thread(EventProcessor.launch, ())
        Utils.thread_counter += 1

        app.run(host=app.config['jimv_listen'], port=app.config['jimv_port'], use_reloader=False, threaded=True)

        while Utils.thread_counter > 0:
            time.sleep(1)

        print 'Main say bye-bye!'

    except:
        logger.error(traceback.format_exc())
        exit(-1)

