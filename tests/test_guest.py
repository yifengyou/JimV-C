#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json
import unittest


__author__ = 'James Iter'
__date__ = '2017/4/4'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class TestGuest(unittest.TestCase):

    base_url = 'http://127.0.0.1:8008/api'
    uuid = ''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # 创建Guest
    @unittest.skip('skip create guest')
    def test_11_create(self):
        payload = {
            "cpu": 4,
            "memory": 4,
            "os_template_id": 1,
            "quantity": 2,
            "name": "",
            "password": "pswd.com",
            "lease_term": 100
        }

        url = TestGuest.base_url + '/guest'
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        self.assertEqual('200', j_r['state']['code'])

    # 获取Guest列表
    def test_12_get(self):
        url = TestGuest.base_url + '/guests'
        headers = {'content-type': 'application/json'}
        r = requests.get(url, headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        TestGuest.uuid = j_r['data'][0]['uuid']
        self.assertEqual('200', j_r['state']['code'])

    # 更新Guest属性
    def test_13_update(self):
        payload = {
            "remark": "zabbix",
        }

        url = TestGuest.base_url + '/guest/' + TestGuest.uuid
        headers = {'content-type': 'application/json'}
        r = requests.patch(url, data=json.dumps(payload), headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        self.assertEqual('200', j_r['state']['code'])

    # 校验更新结果
    def test_14_get(self):
        url = TestGuest.base_url + '/guests'
        headers = {'content-type': 'application/json'}
        r = requests.get(url, headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        self.assertEqual('200', j_r['state']['code'])
        self.assertEqual('zabbix', j_r['data'][0]['remark'])

    # 删除Guest
    # @unittest.skip('skip delete guest')
    def test_15_delete(self):
        url = TestGuest.base_url + '/guests/' + TestGuest.uuid
        headers = {'content-type': 'application/json'}
        r = requests.delete(url, headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        self.assertEqual('200', j_r['state']['code'])


if __name__ == '__main__':
    unittest.main()

