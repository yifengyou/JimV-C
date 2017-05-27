# OS Init

[TOC]: # "目录"

# 目录
- [创建实例初始化操作簇](#创建实例初始化操作簇)
- [更新实例初始化操作簇](#更新实例初始化操作簇)
- [获取实例初始化操作簇列表](#获取实例初始化操作簇列表)
- [删除实例初始化操作簇](#删除实例初始化操作簇)
- [初始化操作内容变量](#初始化操作内容变量)
- [添加初始化操作](#添加初始化操作)
- [获取初始化操作列表](#获取初始化操作列表)
- [更新实例初始化操作](#更新实例初始化操作)
- [删除实例初始化操作](#删除实例初始化操作)


## 创建实例初始化操作簇

> 创建模板被实例化后的初始操作簇

```http
POST https://$domain
  /api/os_init
Body:
{
    "name": "CentOS-Systemd",
    "remark": "用作红帽 Systemd 系列的系统初始化。初始化操作依据 CentOS 7 来实现。"
}
```

| 参数名称 | 必须 |  类型  | 说明 |
|:-------:|:---:|:------:|:-----|
|  name   |  Y  | String | 名称 |
| remark  |  Y  | String | 备注 |

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": {
        "remark": "用作红帽 Systemd 系列的系统初始化。初始化操作依据 CentOS 7 来实现。",
        "id": 1,
        "name": "CentOS-Systemd"
    }
}
```


## 更新实例初始化操作簇

> 更新实例初始操作簇

```http
PATCH https://$domain
  /api/os_init/{os_init_id}
Body:
{
    "name": "CentOS-Systemd",
    "remark": "用作红帽 Systemd 系列的系统初始化。初始化操作依据 CentOS 7 来实现。"
}
```

|  参数名称   | 必须 |  类型  | 说明           |
|:----------:|:---:|:------:|:---------------|
| os_init_id |  Y  |  Long  | 实例初始化簇 ID |
|    name    |  N  | String | 名称           |
|   remark   |  N  | String | 备注           |

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": {
        "remark": "用作红帽 Systemd 系列的系统初始化。初始化操作依据 CentOS 7 来实现。",
        "id": 1,
        "name": "RedHat-Systemd"
    }
}
```


## 获取实例初始化操作簇列表

> 获取实例初始化操作簇列表

```http
GET https://$domain
  /api/os_inits?offset={number}&limit={number}
  or
  /api/os_inits?page={number}&page_size={number}
```

|  参数名称  | 必须 |  类型  | 说明                                        |
|:---------:|:---:|:------:|:--------------------------------------------|
|  offset   |  N  | Number | 偏移量, 默认值0                              |
|   limit   |  N  | Number | 返回条目数量, 默认值50                        |
|   page    |  N  | Number | 页号, 与offset同时存在时, 以offset为准, 默认值1 |
| page_size |  N  | Number | 页大小, 默认值50                             |
| order_by  |  N  | String | 所依据的字段                                 |
|   order   |  N  |  Enum  | 排序策略，`asc`\|`desc`                      |

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": [{
        "remark": "用作红帽 Systemd 系列的系统初始化。初始化操作依据 CentOS 7 来实现。",
        "id": 1,
        "name": "CentOS-Systemd"
    }],
    "paging": {
        "prev": "http://127.0.0.1:8008/api/os_inits?page=1&page_size=50&filter=&order=asc&order_by=id",
        "last": "http://127.0.0.1:8008/api/os_inits?page=1&page_size=50&filter=&order=asc&order_by=id",
        "page_size": 50,
        "next": "http://127.0.0.1:8008/api/os_inits?page=1&page_size=50&filter=&order=asc&order_by=id",
        "limit": 50,
        "offset": 0,
        "total": 1,
        "page": 1,
        "first": "http://127.0.0.1:8008/api/os_inits?page=1&page_size=50&filter=&order=asc&order_by=id"
    }
}
```

| 参数名称 | 必须 |  类型  | 说明 |
|:--------|:---:|:------:|:-----|
| id      |  Y  |  Long  | ID   |
| name    |  Y  | String | 名称 |
| remark  |  Y  | String | 备注 |


## 删除实例初始化操作簇

> 删除指定 id 的实例初始化操作簇

```http
DELETE https://$domain
  /api/os_init/{id}
```

| 参数名称 | 必须 |  类型  | 说明                |
|:--------|:---:|:------:|:--------------------|
| id      |  Y  | String | 实例初始化操作簇的id。 |

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    }
}
```


## 初始化操作内容变量

> 初始化操作时，在内容中可用的变量。最终这些变量，会被替换成全局或当时设定好的内容。

|    变量     | 描述                    |
|:----------:|:-----------------------|
|    {IP}    | Guest 分配到的 IP 地址。 |
| {HOSTNAME} | Guest 分配到的主机名。   |
| {NETMASK}  | 全局定义的子网掩码。      |
| {GATEWAY}  | 全局定义的网关。         |
|   {DNS1}   | 全局定义的 DNS1。        |
|   {DNS2}   | 全局定义的 DNS2。        |


## 添加初始化操作

> 为从模板初始化的实例，添加具体的操作

```http
POST https://$domain
  /api/os_init_write
Body:
{
    "os_init_id": 3,
    "path": "/etc/resolv.conf",
    "content": "\n".join([
        "nameserver {DNS1}",
        "nameserver {DNS2}"
    ])
}
```

|  参数名称   | 必须 |  类型  | 说明                                            |
|:----------:|:---:|:------:|:------------------------------------------------|
| os_init_id |  Y  |  Long  | 初始化操作簇 ID                                  |
|    path    |  Y  | String | 将修改的文件在实例中的路径                         |
|  content   |  Y  | String | 文件内容。内容中可用的变量参见 [初始化操作内容变量](#初始化操作内容变量) |

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": {
        "content": "nameserver {DNS1}\nnameserver {DNS2}",
        "path": "/etc/resolv.conf",
        "id": 1,
        "os_init_id": 3
    }
}
```


## 获取初始化操作列表

> 获取初始化操作列表

```http
GET https://$domain
  /api/os_init_writes?offset={number}&limit={number}
  or
  /api/os_init_writes?page={number}&page_size={number}
```

|  参数名称  | 必须 |  类型  | 说明                                        |
|:---------:|:---:|:------:|:--------------------------------------------|
|  offset   |  N  | Number | 偏移量, 默认值0                              |
|   limit   |  N  | Number | 返回条目数量, 默认值50                        |
|   page    |  N  | Number | 页号, 与offset同时存在时, 以offset为准, 默认值1 |
| page_size |  N  | Number | 页大小, 默认值50                             |
| order_by  |  N  | String | 所依据的字段                                 |
|   order   |  N  |  Enum  | 排序策略，`asc`\|`desc`                      |

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": [{
        "content": "nameserver {DNS1}\nnameserver {DNS2}",
        "path": "/etc/resolv.conf",
        "id": 1,
        "os_init_id": 3
    }],
    "paging": {
        "prev": "http://127.0.0.1:8008/api/os_init_writes?page=1&page_size=50&filter=&order=asc&order_by=id",
        "last": "http://127.0.0.1:8008/api/os_init_writes?page=1&page_size=50&filter=&order=asc&order_by=id",
        "page_size": 50,
        "next": "http://127.0.0.1:8008/api/os_init_writes?page=1&page_size=50&filter=&order=asc&order_by=id",
        "limit": 50,
        "offset": 0,
        "total": 1,
        "page": 1,
        "first": "http://127.0.0.1:8008/api/os_init_writes?page=1&page_size=50&filter=&order=asc&order_by=id"
    }
}
```

| 参数名称    | 必须 |  类型  | 说明           |
|:-----------|:---:|:------:|:---------------|
| id         |  Y  |  Long  | ID             |
| os_init_id |  Y  |  Long  | 实例初始化簇 ID |
| path       |  Y  | String | 初始化的文件路径 |
| content    |  Y  | String | 初始化的文件内容 |


## 更新实例初始化操作

> 更新实例初始操作

```http
PATCH https://$domain
  /api/os_init_write/{os_init_id}
Body:
{
    "path": "/etc/hostname",
    "content": "{HOSTNAME}"
}
```

|  参数名称   | 必须 |  类型  | 说明               |
|:----------:|:---:|:------:|:-------------------|
| os_init_id |  Y  | Number | 初始化操作 ID       |
|    path    |  N  | String | 初始化操作的文件路径 |
|  content   |  N  | String | 初始化操作的文件内容 |

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": {
        "content": "{HOSTNAME}",
        "path": "/etc/hostname",
        "id": 1,
        "os_init_id": 3
    }
}
```

实例初始化操作 信息字段描述参见 [获取初始化操作列表](#获取初始化操作列表)


## 删除实例初始化操作

> 删除指定 id 的实例初始化操作

```http
DELETE https://$domain
  /api/os_init_write/{id}
```

| 参数名称 | 必须 |  类型  | 说明                |
|:--------|:---:|:------:|:--------------------|
| id      |  Y  | Number | 实例初始化操作的id。 |

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    }
}
```


[返回上一级](../README.md)
=====================

