#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
import json
import jimit as ji

from api.base import Base
from models import CPUMemory, Traffic, DiskIO, Utils, Rules


__author__ = 'James Iter'
__date__ = '2017/7/2'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'api_performance',
    __name__,
    url_prefix='/api/performance'
)

blueprints = Blueprint(
    'api_performances',
    __name__,
    url_prefix='/api/performances'
)


cpu_memory = Base(the_class=CPUMemory, the_blueprint=blueprint, the_blueprints=blueprints)
traffic = Base(the_class=Traffic, the_blueprint=blueprint, the_blueprints=blueprints)
disk_io = Base(the_class=DiskIO, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_cpu_memory_get_by_filter():
    return cpu_memory.get_by_filter()


@Utils.dumps2response
def r_traffic_get_by_filter():
    return traffic.get_by_filter()


@Utils.dumps2response
def r_disk_io_get_by_filter():
    return disk_io.get_by_filter()


def get_performance_data(uuid, uuid_field, the_class=None, granularity='hour'):

    args_rules = [
        Rules.UUID.value,
    ]

    try:
        ji.Check.previewing(args_rules, {'uuid': uuid})
        uuids_str = ':'.join([uuid_field, 'in', uuid])

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        max_limit = 10080
        ts = ji.Common.ts()
        _boundary = ts - 60 * 60
        if granularity == 'hour':
            _boundary = ts - 60 * 60

        elif granularity == 'six_hours':
            _boundary = ts - 60 * 60 * 6

        elif granularity == 'day':
            _boundary = ts - 60 * 60 * 24

        elif granularity == 'seven_days':
            _boundary = ts - 60 * 60 * 24 * 7

        else:
            pass

        filter_str = ';'.join([uuids_str, 'timestamp:gt:' + _boundary.__str__()])

        _rows, _rows_count = the_class.get_by_filter(
            offset=0, limit=max_limit, order_by='id', order='asc', filter_str=filter_str)

        def smooth_data(boundary=0, interval=60, now_ts=ji.Common.ts(), rows=None):
            needs = list()
            data = list()

            for t in range(boundary, now_ts, interval):
                needs.append(t - t % interval)

            for row in rows:
                if row['timestamp'] % interval != 0:
                    continue

                if needs.__len__() > 0:
                    t = needs.pop(0)
                else:
                    t = now_ts

                while t < row['timestamp']:
                    data.append({
                        'timestamp': t,
                        'cpu_load': None
                    })

                    if needs.__len__() > 0:
                        t = needs.pop(0)
                    else:
                        t = now_ts

                data.append(row)

            return data

        if granularity == 'day':
            ret['data'] = smooth_data(boundary=_boundary, interval=600, now_ts=ts, rows=_rows)

        if granularity == 'seven_days':
            ret['data'] = smooth_data(boundary=_boundary, interval=600, now_ts=ts, rows=_rows)

        else:
            ret['data'] = smooth_data(boundary=_boundary, interval=60, now_ts=ts, rows=_rows)

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_cpu_memory_last_hour(uuid):
    return get_performance_data(uuid=uuid, uuid_field='guest_uuid', the_class=CPUMemory, granularity='hour')


@Utils.dumps2response
def r_cpu_memory_last_six_hours(uuid):
    return get_performance_data(uuid=uuid, uuid_field='guest_uuid', the_class=CPUMemory, granularity='six_hours')


@Utils.dumps2response
def r_cpu_memory_last_day(uuid):
    return get_performance_data(uuid=uuid, uuid_field='guest_uuid', the_class=CPUMemory, granularity='day')


@Utils.dumps2response
def r_cpu_memory_last_seven_days(uuid):
    return get_performance_data(uuid=uuid, uuid_field='guest_uuid', the_class=CPUMemory, granularity='seven_days')


@Utils.dumps2response
def r_traffic_last_hour(uuid):
    return get_performance_data(uuid=uuid, uuid_field='guest_uuid', the_class=Traffic, granularity='hour')


@Utils.dumps2response
def r_traffic_last_six_hours(uuid):
    return get_performance_data(uuid=uuid, uuid_field='guest_uuid', the_class=Traffic, granularity='six_hours')


@Utils.dumps2response
def r_traffic_last_day(uuid):
    return get_performance_data(uuid=uuid, uuid_field='guest_uuid', the_class=Traffic, granularity='day')


@Utils.dumps2response
def r_traffic_last_seven_days(uuid):
    return get_performance_data(uuid=uuid, uuid_field='guest_uuid', the_class=Traffic, granularity='seven_days')


@Utils.dumps2response
def r_disk_io_last_hour(uuid):
    return get_performance_data(uuid=uuid, uuid_field='disk_uuid', the_class=DiskIO, granularity='hour')


@Utils.dumps2response
def r_disk_io_last_six_hours(uuid):
    return get_performance_data(uuid=uuid, uuid_field='disk_uuid', the_class=DiskIO, granularity='six_hours')


@Utils.dumps2response
def r_disk_io_last_day(uuid):
    return get_performance_data(uuid=uuid, uuid_field='disk_uuid', the_class=DiskIO, granularity='day')


@Utils.dumps2response
def r_disk_io_last_seven_days(uuid):
    return get_performance_data(uuid=uuid, uuid_field='disk_uuid', the_class=DiskIO, granularity='seven_days')


