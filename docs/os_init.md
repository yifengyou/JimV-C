# OS Init

[TOC]: # "目录"

# 目录
- [创建实例初始化操作簇](#创建实例初始化操作簇)
- [更新实例初始化操作簇](#更新实例初始化操作簇)
- [获取实例初始化操作簇列表](#获取实例初始化操作簇列表)
- [删除实例初始化操作簇](#删除实例初始化操作簇)


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


[返回上一级](../README.md)
=====================

