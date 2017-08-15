#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
import json
import jimit as ji
import base64

from api.base import Base
from models import HostCPUMemory, HostTraffic, HostDiskUsageIO, Utils, Rules


__author__ = 'James Iter'
__date__ = '2017/8/7'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'api_host_performance',
    __name__,
    url_prefix='/api/host_performance'
)

blueprints = Blueprint(
    'api_host_performances',
    __name__,
    url_prefix='/api/host_performances'
)


host_cpu_memory = Base(the_class=HostCPUMemory, the_blueprint=blueprint, the_blueprints=blueprints)
host_traffic = Base(the_class=HostTraffic, the_blueprint=blueprint, the_blueprints=blueprints)
host_disk_usage_io = Base(the_class=HostDiskUsageIO, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_cpu_memory_get_by_filter():
    return host_cpu_memory.get_by_filter()


@Utils.dumps2response
def r_traffic_get_by_filter():
    return host_traffic.get_by_filter()


@Utils.dumps2response
def r_disk_usage_io_get_by_filter():
    return host_disk_usage_io.get_by_filter()


def get_performance_data(node_id, the_class=None, nic_name=None, mountpoint=None, granularity='hour'):

    args_rules = [
        Rules.NODE_ID.value,
    ]

    filters = list()

    try:
        ji.Check.previewing(args_rules, {'node_id': node_id})

        node_ids_str = 'node_id:in:' + node_id.__str__()
        filters.append(node_ids_str)

        if nic_name is not None:
            filters.append('name:eq:' + nic_name)

        if mountpoint is not None:
            filters.append('mountpoint:eq:' + mountpoint)

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

        filters.append('timestamp:gt:' + _boundary.__str__())

        filter_str = ';'.join(filters)

        _rows, _rows_count = the_class.get_by_filter(
            offset=0, limit=max_limit, order_by='id', order='asc', filter_str=filter_str)

        def smooth_data(boundary=0, interval=60, now_ts=ji.Common.ts(), rows=None):
            needs = list()
            data = list()

            for t in range(boundary + interval, now_ts, interval):
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
                        'cpu_load': None,
                        'memory_available': None,
                        'rx_packets': None,
                        'rx_bytes': None,
                        'tx_packets': None,
                        'tx_bytes': None,
                        'rd_req': None,
                        'rd_bytes': None,
                        'used': None,
                        'wr_req': None,
                        'wr_bytes': None
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
def r_cpu_memory_last_hour(node_id):
    return get_performance_data(node_id=node_id, the_class=HostCPUMemory, granularity='hour')


@Utils.dumps2response
def r_cpu_memory_last_six_hours(node_id):
    return get_performance_data(node_id=node_id, the_class=HostCPUMemory, granularity='six_hours')


@Utils.dumps2response
def r_cpu_memory_last_day(node_id):
    return get_performance_data(node_id=node_id, the_class=HostCPUMemory, granularity='day')


@Utils.dumps2response
def r_cpu_memory_last_seven_days(node_id):
    return get_performance_data(node_id=node_id, the_class=HostCPUMemory, granularity='seven_days')


@Utils.dumps2response
def r_traffic_last_hour(node_id, nic_name):
    return get_performance_data(node_id=node_id, nic_name=nic_name, the_class=HostTraffic, granularity='hour')


@Utils.dumps2response
def r_traffic_last_six_hours(node_id, nic_name):
    return get_performance_data(node_id=node_id, nic_name=nic_name, the_class=HostTraffic, granularity='six_hours')


@Utils.dumps2response
def r_traffic_last_day(node_id, nic_name):
    return get_performance_data(node_id=node_id, nic_name=nic_name, the_class=HostTraffic, granularity='day')


@Utils.dumps2response
def r_traffic_last_seven_days(node_id, nic_name):
    return get_performance_data(node_id=node_id, nic_name=nic_name, the_class=HostTraffic, granularity='seven_days')


@Utils.dumps2response
def r_disk_usage_io_last_hour(node_id, mountpoint):
    mountpoint = base64.b64decode(mountpoint)
    return get_performance_data(node_id=node_id, mountpoint=mountpoint, the_class=HostDiskUsageIO, granularity='hour')


@Utils.dumps2response
def r_disk_usage_io_last_six_hours(node_id, mountpoint):
    mountpoint = base64.b64decode(mountpoint)
    return get_performance_data(node_id=node_id, mountpoint=mountpoint, the_class=HostDiskUsageIO,
                                granularity='six_hours')


@Utils.dumps2response
def r_disk_usage_io_last_day(node_id, mountpoint):
    mountpoint = base64.b64decode(mountpoint)
    return get_performance_data(node_id=node_id, mountpoint=mountpoint, the_class=HostDiskUsageIO, granularity='day')


@Utils.dumps2response
def r_disk_usage_io_last_seven_days(node_id, mountpoint):
    mountpoint = base64.b64decode(mountpoint)
    return get_performance_data(node_id=node_id, mountpoint=mountpoint, the_class=HostDiskUsageIO,
                                granularity='seven_days')


