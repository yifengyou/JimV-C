#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request
import json
import jimit as ji

from api.base import Base
from models import Guest
from models import Snapshot, SnapshotDiskMapping
from models import Utils
from models import Rules


__author__ = 'James Iter'
__date__ = '2018/4/10'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'api_snapshot',
    __name__,
    url_prefix='/api/snapshot'
)

blueprints = Blueprint(
    'api_snapshots',
    __name__,
    url_prefix='/api/snapshots'
)


snapshot_base = Base(the_class=Snapshot, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    args_rules = [
        Rules.GUEST_UUID.value
    ]

    if 'label' in request.json:
        args_rules.append(
            Rules.LABEL.value,
        )

    try:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        ji.Check.previewing(args_rules, request.json)

        snapshot = Snapshot()
        guest = Guest()
        guest.uuid = request.json.get('guest_uuid')
        guest.get_by('uuid')

        snapshot.label = request.json.get('label', '')
        snapshot.status = guest.status
        snapshot.guest_uuid = guest.uuid
        snapshot.snapshot_id = '_'.join(['tmp', ji.Common.generate_random_code(length=8)])
        snapshot.parent_id = '-'
        snapshot.progress = 0

        snapshot.create()
        snapshot.get_by('snapshot_id')

        message = {
            '_object': 'snapshot',
            'action': 'create',
            'uuid': guest.uuid,
            'node_id': guest.node_id,
            'passback_parameters': {'id': snapshot.id}
        }

        Utils.emit_instruction(message=json.dumps(message, ensure_ascii=False))

        ret['data'] = snapshot.__dict__
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(snapshot_id):

    snapshot = Snapshot()

    args_rules = [
        Rules.SNAPSHOT_ID.value
    ]

    if 'label' in request.json:
        args_rules.append(
            Rules.LABEL.value,
        )

    if args_rules.__len__() < 2:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    request.json['snapshot_id'] = snapshot_id

    try:
        ji.Check.previewing(args_rules, request.json)
        snapshot.snapshot_id = request.json.get('snapshot_id')

        snapshot.get_by('snapshot_id')
        snapshot.label = request.json.get('label', snapshot.label)

        snapshot.update()
        snapshot.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = snapshot.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get(snapshots_id):
    return snapshot_base.get(ids=snapshots_id, ids_rule=Rules.SNAPSHOTS_ID.value, by_field='snapshot_id')


@Utils.dumps2response
def r_get_by_filter():
    return snapshot_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return snapshot_base.content_search()


@Utils.dumps2response
def r_delete(snapshots_id):

    args_rules = [
        Rules.SNAPSHOTS_ID.value
    ]

    try:
        ji.Check.previewing(args_rules, {'snapshots_id': snapshots_id})

        snapshot = Snapshot()
        guest = Guest()

        # 检测所指定的 快照 都存在
        for snapshot_id in snapshots_id.split(','):
            snapshot.snapshot_id = snapshot_id
            snapshot.get_by('snapshot_id')

            guest.uuid = snapshot.guest_uuid
            guest.get_by('uuid')

        # 执行删除操作
        for snapshot_id in snapshots_id.split(','):
            snapshot.snapshot_id = snapshot_id
            snapshot.get_by('snapshot_id')

            guest.uuid = snapshot.guest_uuid
            guest.get_by('uuid')

            message = {
                '_object': 'snapshot',
                'action': 'delete',
                'uuid': snapshot.guest_uuid,
                'snapshot_id': snapshot.snapshot_id,
                'node_id': guest.node_id,
                'passback_parameters': {'id': snapshot.id}
            }

            Utils.emit_instruction(message=json.dumps(message))

            # 删除创建失败的 快照
            if snapshot.progress == 255:
                SnapshotDiskMapping.delete_by_filter(filter_str=':'.join(['snapshot_id', 'eq', snapshot.snapshot_id]))
                snapshot.delete()

            else:
                snapshot.progress = 254
                snapshot.update()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_revert(snapshot_id):

    args_rules = [
        Rules.SNAPSHOT_ID.value
    ]

    try:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        ji.Check.previewing(args_rules, {'snapshot_id': snapshot_id})

        snapshot = Snapshot()
        guest = Guest()

        snapshot.snapshot_id = snapshot_id
        snapshot.get_by('snapshot_id')
        snapshot.progress = 253
        snapshot.update()
        snapshot.get()

        guest.uuid = snapshot.guest_uuid
        guest.get_by('uuid')

        message = {
            '_object': 'snapshot',
            'action': 'revert',
            'uuid': guest.uuid,
            'snapshot_id': snapshot.snapshot_id,
            'node_id': guest.node_id,
            'passback_parameters': {'id': snapshot.id}
        }

        Utils.emit_instruction(message=json.dumps(message, ensure_ascii=False))

        ret['data'] = snapshot.__dict__
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)

