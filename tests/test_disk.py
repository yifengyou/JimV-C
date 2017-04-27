#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json
import unittest


__author__ = 'James Iter'
__date__ = '2017/4/27'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class TestDisk(unittest.TestCase):

    base_url = 'http://127.0.0.1:8008/api'
    uuid = ''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # 创建 Disk
    def test_11_create(self):
        payload = {
            "size": 10
        }

        url = TestDisk.base_url + '/disk'
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        self.assertEqual('200', j_r['state']['code'])

    def test_12_get(self):
        pass

    def test_13_update(self):
        pass

    # 校验更新结果
    def test_14_get(self):
        pass

    # 删除Guest
    # @unittest.skip('skip delete guest')
    def test_15_delete(self):
        pass


if __name__ == '__main__':
    unittest.main()
