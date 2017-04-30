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
    new_size = 200
    uuid_list = list()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # # 创建 Disk
    # def test_11_create(self):
    #     payload = {
    #         "size": 10
    #     }
    #
    #     url = TestDisk.base_url + '/disk'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.post(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # def test_12_get(self):
    #     url = TestDisk.base_url + '/disks'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.get(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     TestDisk.uuid = j_r['data'][0]['uuid']
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # # @unittest.skip('skip resize disk')
    # def test_13_disk_resize(self):
    #     url = TestDisk.base_url + '/disk/_disk_resize/' + TestDisk.uuid + '/' + TestDisk.new_size.__str__()
    #     headers = {'content-type': 'application/json'}
    #     r = requests.put(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # # @unittest.skip('skip update disk')
    # def test_14_update(self):
    #     payload = {
    #         "label": "Hello-disk"
    #     }
    #
    #     url = TestDisk.base_url + '/disk/' + TestDisk.uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.patch(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # # 校验更新结果
    # # @unittest.skip('skip get disk')
    # def test_15_get(self):
    #     url = TestDisk.base_url + '/disks'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.get(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #     self.assertEqual(TestDisk.new_size, j_r['data'][0]['size'])
    #     self.assertEqual('Hello-disk', j_r['data'][0]['label'])
    #     for disk in j_r['data']:
    #         TestDisk.uuid_list.append(disk['uuid'])

    def test_16_detach_disk(self):
        url = TestDisk.base_url + '/guest/_detach_disk/' + '49aab662-abdd-4338-bcde-60a70020daa0'
        headers = {'content-type': 'application/json'}
        r = requests.put(url, headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        self.assertEqual('200', j_r['state']['code'])

    # 删除Guest
    # @unittest.skip('skip delete disk')
    def test_17_delete(self):
        TestDisk.uuid_list.append('49aab662-abdd-4338-bcde-60a70020daa0')
        for uuid in TestDisk.uuid_list:
            TestDisk.uuid = uuid
            url = TestDisk.base_url + '/disk/' + TestDisk.uuid
            headers = {'content-type': 'application/json'}
            r = requests.delete(url, headers=headers)
            j_r = json.loads(r.content)
            print json.dumps(j_r, ensure_ascii=False)
            self.assertEqual('200', j_r['state']['code'])


if __name__ == '__main__':
    unittest.main()
