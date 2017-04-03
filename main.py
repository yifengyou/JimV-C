#!/usr/bin/env python
# -*- coding: utf-8 -*-


import traceback
import thread

from models.initialize import app, logger
import route_table
from models import Database as db
from views.os_init import blueprint as os_init_blueprint
from views.os_init_write import blueprint as os_init_write_blueprint
from views.os_template import blueprint as os_template_blueprint
from views.guest import blueprint as guest_blueprint
from views.config import blueprint as config_blueprint


__author__ = 'James Iter'
__date__ = '2017/3/31'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


# noinspection PyBroadException
try:
    db.init_conn_mysql()
    thread.start_new_thread(db.keepalived_mysql, ())
    db.init_conn_redis()

    app.register_blueprint(os_init_blueprint)
    app.register_blueprint(os_init_write_blueprint)
    app.register_blueprint(os_template_blueprint)
    app.register_blueprint(guest_blueprint)
    app.register_blueprint(config_blueprint)
except:
    logger.error(traceback.format_exc())

if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        app.run(host=app.config['jimv_listen'], port=app.config['jimv_port'], use_reloader=False, threaded=True)
    except:
        logger.error(traceback.format_exc())
