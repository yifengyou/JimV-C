#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json
import unittest


__author__ = 'James Iter'
__date__ = '2017/3/31'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class TestOSInit(unittest.TestCase):

    base_url = 'http://127.0.0.1:8008/api'
    boot_job_id = 0

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # 创建系统初始化组
    def test_11_create(self):
        payload = {
            "name": 'CentOS-Systemd',
            "use_for": 0,
            "remark": u'用作红帽 Systemd 系列的系统初始化。初始化操作依据 CentOS 7 来实现。'
        }

        url = TestOSInit.base_url + '/boot_job'
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        self.assertEqual('200', j_r['state']['code'])

    # 获取系统初始化组列表
    def test_12_get(self):
        url = TestOSInit.base_url + '/boot_jobs'
        headers = {'content-type': 'application/json'}
        r = requests.get(url, headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        TestOSInit.boot_job_id = j_r['data'][0]['id']
        self.assertEqual('200', j_r['state']['code'])

    # 创建更新系统初始化组
    def test_13_update(self):
        payload = {
            "name": 'RedHat-Systemd'
        }

        url = TestOSInit.base_url + '/boot_job/' + TestOSInit.boot_job_id.__str__()
        headers = {'content-type': 'application/json'}
        r = requests.patch(url, data=json.dumps(payload), headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        self.assertEqual('200', j_r['state']['code'])

    # 校验系统初始化组列表更新结果
    def test_14_get(self):
        url = TestOSInit.base_url + '/boot_jobs'
        headers = {'content-type': 'application/json'}
        r = requests.get(url, headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        self.assertEqual('200', j_r['state']['code'])
        self.assertEqual('RedHat-Systemd', j_r['data'][0]['name'])

    # # 删除系统初始化组列表更新结果
    # def test_15_delete(self):
    #     url = TestOSInit.base_url + '/boot_jobs/' + TestOSInit.boot_job_id.__str__()
    #     headers = {'content-type': 'application/json'}
    #     r = requests.delete(url, headers=headers)
    #     j_r = json.loads(r.content)
    #     print json.dumps(j_r, ensure_ascii=False)
    #     self.assertEqual('200', j_r['state']['code'])

    def test_21_create(self):
        payload = {
            "name": 'Gentoo-OpenRC',
            "use_for": 0,
            "remark": u'Gentoo startup process。'
        }

        url = TestOSInit.base_url + '/boot_job'
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        self.assertEqual('200', j_r['state']['code'])

    # 创建系统初始化组
    def test_22_create(self):
        payload = {
            "name": 'Ubuntu-Upstart',
            "use_for": 0,
            "remark": u'Ubuntu startup process。'
        }

        url = TestOSInit.base_url + '/boot_job'
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        self.assertEqual('200', j_r['state']['code'])

    # 创建系统初始化组
    def test_23_create(self):
        payload = {
            "name": 'CentOS-SysV',
            "use_for": 0,
            "remark": u'用作CentOS SysV 系列的系统初始化。初始化操作依据 CentOS 6.8 来实现。'
        }

        url = TestOSInit.base_url + '/boot_job'
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        j_r = json.loads(r.content)
        print json.dumps(j_r, ensure_ascii=False)
        self.assertEqual('200', j_r['state']['code'])

if __name__ == '__main__':
    unittest.main()

