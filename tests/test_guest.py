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
    disk_uuid = ''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # 创建Guest
    # @unittest.skip('skip create guest')
    # def test_11_create(self):
    #     payload = {
    #         "cpu": 4,
    #         "memory": 4,
    #         "os_template_id": 1,
    #         "quantity": 1,
    #         "name": "",
    #         "password": "pswd.com",
    #         "lease_term": 100
    #     }
    #
    #     url = TestGuest.base_url + '/guest'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.post(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    # 获取 Guest 列表
    # def test_12_get_list(self):
    #     url = TestGuest.base_url + '/guests'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.get(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     TestGuest.uuid = j_r['data'][-1]['uuid']
    #     self.assertEqual('200', j_r['state']['code'])

    # # 获取指定 Guest
    # def test_13_get(self):
    #     url = TestGuest.base_url + '/guest/' + TestGuest.uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.get(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # # 更新Guest属性
    # def test_14_update(self):
    #     payload = {
    #         "remark": "zabbix",
    #     }
    #
    #     url = TestGuest.base_url + '/guest/' + TestGuest.uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.patch(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # # 校验更新结果
    # def test_15_get(self):
    #     url = TestGuest.base_url + '/guest/' + TestGuest.uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.get(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #     self.assertEqual('zabbix', j_r['data']['remark'])

    # # 创建 Disk
    # def test_21_create_disk(self):
    #     payload = {
    #         "size": 10
    #     }
    #
    #     url = TestGuest.base_url + '/disk'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.post(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # def test_22_get_disks(self):
    #     url = TestGuest.base_url + '/disks'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.get(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     TestGuest.disk_uuid = j_r['data'][-1]['uuid']
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # # @unittest.skip('skip resize disk')
    # def test_23_disk_resize(self):
    #     url = TestGuest.base_url + '/disk/_disk_resize/' + TestGuest.disk_uuid + '/2000'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.put(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # def test_31_attach_disk(self):
    #     TestGuest.uuid = 'ba102b41-4e7a-4d5b-a9e0-43d162695e4a'
    #     TestGuest.disk_uuid = 'c5881400-4f98-49a8-b5cf-afb5956a5a4b'
    #     url = TestGuest.base_url + '/guest/_attach_disk/' + TestGuest.uuid + '/' + TestGuest.disk_uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.put(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    # def test_32_detach_disk(self):
    #     url = TestGuest.base_url + '/guest/_detach_disk/' + TestGuest.disk_uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.put(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # # 删除Guest
    # # @unittest.skip('skip delete guest')
    # def test_41_delete(self):
    #     url = TestGuest.base_url + '/guests/' + TestGuest.uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.delete(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # def test_42_delete_disk(self):
    #     url = TestGuest.base_url + '/disk/' + TestGuest.disk_uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.delete(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # def test_51_reboot(self):
    #     url = TestGuest.base_url + '/guests/_reboot/' + TestGuest.uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.put(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # def test_52_force_reboot(self):
    #     url = TestGuest.base_url + '/guests/_force_reboot/' + TestGuest.uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.put(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    # def test_53_shutdown(self):
    #     url = TestGuest.base_url + '/guests/_shutdown/' + TestGuest.uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.put(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    # def test_54_force_shutdown(self):
    #     url = TestGuest.base_url + '/guests/_force_shutdown/' + TestGuest.uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.put(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    # def test_55_boot(self):
    #     url = TestGuest.base_url + '/guests/_boot/' + TestGuest.uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.put(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    # def test_56_suspend(self):
    #     url = TestGuest.base_url + '/guests/_suspend/' + TestGuest.uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.put(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    # def test_57_resume(self):
    #     url = TestGuest.base_url + '/guests/_resume/' + TestGuest.uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.put(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)

    # def test_58_attach_disk(self):
    #     TestGuest.disk_uuid = '234670cb-3ce4-4ef9-ba23-12bed636184c'
    #     url = TestGuest.base_url + '/guest/_attach_disk/' + TestGuest.uuid + '/' + TestGuest.disk_uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.put(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    # def test_59_detach_disk(self):
    #     TestGuest.disk_uuid = '234670cb-3ce4-4ef9-ba23-12bed636184c'
    #     url = TestGuest.base_url + '/guest/_detach_disk/' + TestGuest.disk_uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.put(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    # def test_60_delete(self):
    #     url = TestGuest.base_url + '/guests/' + TestGuest.uuid
    #     headers = {'content-type': 'application/json'}
    #     r = requests.delete(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    # def test_61_migrate(self):
    #     url = TestGuest.base_url + '/guests/_migrate/' + TestGuest.uuid + '/10k02.jkser.com'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.put(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    def test_62_content_search(self):
        url = TestGuest.base_url + '/guests/_search?keyword=10.10.4'
        headers = {'content-type': 'application/json'}
        r = requests.get(url, headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        self.assertEqual('200', j_r['state']['code'])


if __name__ == '__main__':
    unittest.main()

