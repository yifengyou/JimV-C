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
    os_init_id = 0

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # 创建Guest
    def test_11_create(self):
        payload = {
            "cpu": 4,
            "memory": 4,
            "os_template_id": 5,
            "disks": [],
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
        pass

    # 更新Guest属性
    def test_13_update(self):
        pass

    # 校验更新结果
    def test_14_get(self):
        pass

    # 删除Guest
    def test_15_delete(self):
        pass


if __name__ == '__main__':
    unittest.main()

