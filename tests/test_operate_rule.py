#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json
import unittest


__author__ = 'James Iter'
__date__ = '2017/3/31'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class TestOperateRule(unittest.TestCase):

    base_url = 'http://127.0.0.1:8008/api'
    boot_job_id = 2
    operate_rule_id = 0

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # # 创建系统初始化组
    # def test_11_create(self):
    #     payload = {
    #         "name": "CentOS-Systemd",
    #         "use_for": 0,
    #         "remark": u"用作红帽 Systemd 系列的系统初始化。初始化操作依据 CentOS 7 来实现。"
    #     }
    #
    #     url = TestOperateRule.base_url + '/boot_job'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.post(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     TestOperateRule.boot_job_id = j_r['data']['id']
    #     self.assertEqual('200', j_r['state']['code'])

    # # 添加系统初始化操作
    # def test_21_create(self):
    #     payload = {
    #         "boot_job_id": TestOperateRule.boot_job_id,
    #         "kind": 1,
    #         "path": "/etc/resolv.conf",
    #         "content": "\n".join([
    #             "nameserver {DNS1}",
    #             "nameserver {DNS2}"
    #         ])
    #     }
    #
    #     url = TestOperateRule.base_url + '/operate_rule'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.post(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # # 添加系统初始化操作
    # def test_22_create(self):
    #     payload = {
    #         "boot_job_id": TestOperateRule.boot_job_id,
    #         "kind": 1,
    #         "path": "/etc/sysconfig/network-scripts/ifcfg-eth0",
    #         "content": "\n".join([
    #             "DEVICE=eth0",
    #             "TYPE=Ethernet",
    #             "ONBOOT=yes",
    #             "BOOTPROTO=\"static\"",
    #             "IPADDR={IP}",
    #             "NETMASK={NETMASK}",
    #             "GATEWAY={GATEWAY}",
    #             "DNS1={DNS1}",
    #             "DNS2={DNS2}",
    #             "IPV6INIT=no",
    #             "NAME=eth0"
    #         ])
    #     }
    #
    #     url = TestOperateRule.base_url + '/operate_rule'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.post(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # # 添加系统初始化操作
    # def test_23_create(self):
    #     payload = {
    #         "boot_job_id": TestOperateRule.boot_job_id,
    #         "kind": 1,
    #         "path": "/etc/hostname",
    #         "content": "hostname"
    #     }
    #
    #     url = TestOperateRule.base_url + '/operate_rule'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.post(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     TestOperateRule.operate_rule_id = j_r['data']['id']
    #     self.assertEqual('200', j_r['state']['code'])

    # def test_25_get_list(self):
    #     url = TestOperateRule.base_url + '/operate_rules'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.get(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # def test_26_update(self):
    #     payload = {
    #         "path": "/etc/hostname",
    #         "content": "{HOSTNAME}"
    #     }
    #
    #     url = TestOperateRule.base_url + '/operate_rule/' + TestOperateRule.operate_rule_id.__str__()
    #     headers = {'content-type': 'application/json'}
    #     r = requests.patch(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    # @unittest.skip('skip delete os init write!')
    # def test_27_delete(self):
    #     url = TestOperateRule.base_url + '/operate_rules/' + TestOperateRule.operate_rule_id.__str__()
    #     headers = {'content-type': 'application/json'}
    #     r = requests.delete(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # @unittest.skip('skip delete os init!')
    # # 删除系统初始化组列表更新结果
    # def test_31_delete(self):
    #     url = TestOperateRule.base_url + '/boot_jobs/' + TestOperateRule.boot_job_id.__str__()
    #     headers = {'content-type': 'application/json'}
    #     r = requests.delete(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # def test_51_create(self):
    #     payload = {
    #         "boot_job_id": 5,
    #         "kind": 1,
    #         "path": "/etc/resolv.conf",
    #         "content": "\n".join([
    #             "nameserver {DNS1}",
    #             "nameserver {DNS2}"
    #         ])
    #     }
    #
    #     url = TestOperateRule.base_url + '/operate_rule'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.post(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # def test_52_create(self):
    #     payload = {
    #         "boot_job_id": 5,
    #         "kind": 1,
    #         "path": "/etc/sysconfig/network-scripts/ifcfg-eth0",
    #         "content": "\n".join([
    #             "DEVICE=eth0",
    #             "TYPE=Ethernet",
    #             "ONBOOT=yes",
    #             "BOOTPROTO=\"static\"",
    #             "IPADDR={IP}",
    #             "NETMASK={NETMASK}",
    #             "GATEWAY={GATEWAY}",
    #             "IPV6INIT=no",
    #             "NAME=eth0"
    #         ])
    #     }
    #
    #     url = TestOperateRule.base_url + '/operate_rule'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.post(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # def test_53_create(self):
    #     payload = {
    #         "boot_job_id": 5,
    #         "kind": 1,
    #         "path": "/etc/sysconfig/network",
    #         "content": "\n".join([
    #             "NETWORKING=yes",
    #             "HOSTNAME=\"{HOSTNAME}\""
    #         ])
    #     }
    #
    #     url = TestOperateRule.base_url + '/operate_rule'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.post(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     TestOperateRule.operate_rule_id = j_r['data']['id']
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # def test_61_create(self):
    #     payload = {
    #         "boot_job_id": 3,
    #         "kind": 1,
    #         "path": "/etc/resolv.conf",
    #         "content": "\n".join([
    #             "nameserver {DNS1}",
    #             "nameserver {DNS2}"
    #         ])
    #     }
    #
    #     url = TestOperateRule.base_url + '/operate_rule'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.post(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # def test_62_create(self):
    #     payload = {
    #         "boot_job_id": 3,
    #         "kind": 1,
    #         "path": "/etc/conf.d/net",
    #         "content": "\n".join([
    #             "config_eth0=\"{IP}/{NETMASK}\"",
    #             "routes_eth0=\"default via {GATEWAY}\""
    #         ])
    #     }
    #
    #     url = TestOperateRule.base_url + '/operate_rule'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.post(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])
    #
    # def test_63_create(self):
    #     payload = {
    #         "boot_job_id": 3,
    #         "kind": 1,
    #         "path": "/etc/conf.d/hostname",
    #         "content": "hostname=\"{HOSTNAME}\""
    #     }
    #
    #     url = TestOperateRule.base_url + '/operate_rule'
    #     headers = {'content-type': 'application/json'}
    #     r = requests.post(url, data=json.dumps(payload), headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     TestOperateRule.operate_rule_id = j_r['data']['id']
    #     self.assertEqual('200', j_r['state']['code'])

if __name__ == '__main__':
    unittest.main()

