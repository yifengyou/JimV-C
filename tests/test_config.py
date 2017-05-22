#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json
import unittest


__author__ = 'James Iter'
__date__ = '2017/4/3'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class TestConfig(unittest.TestCase):

    base_url = 'http://127.0.0.1:8008/api'
    config_id = 0

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # # 创建 JimV 配置
    # def test_11_create(self):
    #     payload = {
    #         "glusterfs_volume": "gv0",
    #         "vm_network": "net-br0",
    #         "vm_manage_network": "net-br0",
    #         "start_ip": "10.10.3.1",
    #         "end_ip": "10.10.6.254",
    #         "start_vnc_port": 15900,
    #         "netmask": "255.255.240.0",
    #         "gateway": "10.10.15.254",
    #         "dns1": "10.1.17.1",
    #         "dns2": "223.5.5.5",
    #         "rsa_private": "",
    #         "rsa_public": ""
    #     }
    #
    #     url = TestConfig.base_url + '/config'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.post(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     TestConfig.config_id = j_r['data']['id']
    #     self.assertEqual('200', j_r['state']['code'])

    # 获取配置
    # def test_12_get(self):
    #     url = TestConfig.base_url + '/config'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.get(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    # # 更新配置
    # def test_13_update(self):
    #     payload = {
    #         "glusterfs_volume": "gv0",
    #         "vm_network": "net-br0",
    #         "vm_manage_network": "net-br0",
    #         "start_ip": "10.10.7.1",
    #         "end_ip": "10.10.9.254",
    #         "start_vnc_port": 15900,
    #         "netmask": "255.255.240.0",
    #         "gateway": "10.10.15.254",
    #         "dns1": "223.5.5.5",
    #         "dns2": "8.8.8.8",
    #         "rsa_public": "what?",
    #         "rsa_private": ""
    #     }
    #
    #     url = TestConfig.base_url + '/config'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.patch(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    # # 校验更新结果
    # def test_14_get(self):
    #     url = TestConfig.base_url + '/config'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.get(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #     self.assertEqual('what?', j_r['data']['rsa_public'])
    #
    # # 删除配置
    # def test_15_delete(self):
    #     url = TestConfig.base_url + '/config'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.delete(url, headers=headers)
    #     self.assertEqual(405, r.status_code)


if __name__ == '__main__':
    unittest.main()

