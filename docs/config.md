# Config

[TOC]: # "目录"

# 目录
- [初始化配置](#初始化配置)
- [获取配置信息](#获取配置信息)
- [更新配置信息](#更新配置信息)


## 初始化配置

> 初始化 JimV 系统配置，只能执行一次。后面要更改，需通过更新接口操作。

```http
POST https://$domain
  /api/config
Body:
{
    "glusterfs_volume": "gv0",
    "vm_network": "net-br0",
    "vm_manage_network": "net-br0",
    "start_ip": "10.10.3.1",
    "end_ip": "10.10.6.254",
    "start_vnc_port": 15900,
    "netmask": "255.255.240.0",
    "gateway": "10.10.15.254",
    "dns1": "10.1.17.1",
    "dns2": "223.5.5.5",
    "rsa_private": "",
    "rsa_public": ""
}
```

|      参数名称      | 必须 |  类型  | 说明                                       |
|:-----------------:|:---:|:------:|:-------------------------------------------|
| glusterfs_volume  |  Y  | String | 分配给 JimV 使用的 GlusterFS 卷              |
|    vm_network     |  Y  | String | 虚拟机使用的网络                             |
| vm_manage_network |  Y  | String | 管理虚拟机的带外网络                         |
|     start_ip      |  Y  | String | 虚拟化环境中，分配给虚拟机的起始 IP            |
|      end_ip       |  Y  | String | 虚拟化环境中，分配给虚拟机的截止 IP            |
|  start_vnc_port   |  Y  | String | 从宿主机分配给虚拟机的起始 VNC 端口            |
|      netmask      |  Y  | String | 分配给虚拟机的子网掩码                        |
|      gateway      |  Y  | String | 分配给虚拟机的网关                           |
|       dns1        |  Y  | String | 分配给虚拟机的首 DNS 服务器地址               |
|       dns2        |  Y  | String | 分配给虚拟机的备用 DNS 服务器地址              |
|    rsa_private    |  Y  | String | 全局管理员，管理虚拟机时，所使用的 SSH RSA 私钥 |
|    rsa_public     |  Y  | String | 注入进虚拟机的 SSH RSA  公钥                 |

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": {
        "vm_manage_network": "net-br0",
        "dns2": "223.5.5.5",
        "dns1": "10.1.17.1",
        "gateway": "10.10.15.254",
        "netmask": "255.255.240.0",
        "end_ip": "10.10.6.254",
        "glusterfs_volume": "gv0",
        "rsa_private": "",
        "vm_network": "net-br0",
        "start_ip": "10.10.3.1",
        "rsa_public": "",
        "start_vnc_port": 15900,
        "id": 1
    }
}
```


## 获取配置信息

> 获取 JimV 的配置信息

```http
GET https://$domain
  /api/config
```

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": {
        "vm_manage_network": "net-br0",
        "dns2": "223.5.5.5",
        "dns1": "10.1.17.1",
        "gateway": "10.10.15.254",
        "netmask": "255.255.240.0",
        "end_ip": "10.10.6.254",
        "glusterfs_volume": "gv0",
        "rsa_private": "",
        "vm_network": "net-br0",
        "start_ip": "10.10.3.1",
        "rsa_public": "",
        "start_vnc_port": 15900,
        "id": 1
    }
}
```

|      参数名称      | 必须 |  类型  | 说明                                       |
|:-----------------:|:---:|:------:|:-------------------------------------------|
|        id         |  Y  |  Long  | 配置id                                     |
| glusterfs_volume  |  Y  | String | 分配给 JimV 使用的 GlusterFS 卷              |
|    vm_network     |  Y  | String | 虚拟机使用的网络                             |
| vm_manage_network |  Y  | String | 管理虚拟机的带外网络                         |
|     start_ip      |  Y  | String | 虚拟化环境中，分配给虚拟机的起始 IP            |
|      end_ip       |  Y  | String | 虚拟化环境中，分配给虚拟机的截止 IP            |
|  start_vnc_port   |  Y  |  Long  | 从宿主机分配给虚拟机的起始 VNC 端口            |
|      netmask      |  Y  | String | 分配给虚拟机的子网掩码                        |
|      gateway      |  Y  | String | 分配给虚拟机的网关                           |
|       dns1        |  Y  | String | 分配给虚拟机的首 DNS 服务器地址               |
|       dns2        |  Y  | String | 分配给虚拟机的备用 DNS 服务器地址              |
|    rsa_private    |  Y  | String | 全局管理员，管理虚拟机时，所使用的 SSH RSA 私钥 |
|    rsa_public     |  Y  | String | 注入进虚拟机的 SSH RSA  公钥                 |


## 更新配置信息

> 更新 JimV 的配置

```http
PATCH https://$domain
  /api/config
Body:
{
    "glusterfs_volume": "gv0",
    "vm_network": "net-br0",
    "vm_manage_network": "net-br0",
    "start_ip": "10.10.7.1",
    "end_ip": "10.10.9.254",
    "start_vnc_port": 15900,
    "netmask": "255.255.240",
    "gateway": "10.10.15.254",
    "dns1": "2223.5.5.5",
    "dns2": "8.8.8.8",
    "rsa_public": "what?",
    "rsa_private": ""
}
```

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": {
        "vm_manage_network": "net-br0",
        "dns2": "8.8.8.8",
        "dns1": "223.5.5.5",
        "id": 1,
        "netmask": "255.255.240.0",
        "end_ip": "10.10.9.254",
        "glusterfs_volume": "gv0",
        "rsa_private": "",
        "vm_network": "net-br0",
        "start_ip": "10.10.7.1",
        "rsa_public": "what?",
        "start_vnc_port": 15900,
        "gateway": "10.10.15.254"
    }
}
```

配置信息字段描述参见 [获取配置信息](#获取配置信息)


