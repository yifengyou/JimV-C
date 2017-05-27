# OS Template

[TOC]: # "目录"

# 目录
- [添加系统模板](#添加系统模板)
- [获取系统模板列表](#获取系统模板列表)
- [更改系统模板信息](#更改系统模板信息)
- [删除系统模板](#删除系统模板)


## 添加系统模板

>  添加系统模板记录

```http
POST https://$domain
  /api/os_template
Body:
{
    "label": "CentOS-7.2",
    "name": "centos72_multi-user_2016-09-15_128G.qcow2",
    "active": True,
    "os_init_id": 3
}
```

|  参数名称   | 必须 |  类型   | 说明              |
|:----------:|:---:|:-------:|:------------------|
|   label    |  Y  | String  | 标识              |
|    name    |  Y  | String  | 路径中的模板名称    |
|   active   |  Y  | Boolean | 是否可用           |
| os_init_id |  N  |  Long   | 实例初始化操作簇 ID |

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": {
        "active": 1,
        "os_init_id": 3,
        "id": 1,
        "name": "centos72_multi-user_2016-09-15_128G.qcow2",
        "label": "CentOS-7.2"
    }
}
```

## 获取系统模板列表

> 获取系统模板列表

```http
GET https://$domain
  /api/os_templates?offset={number}&limit={number}
  or
  /api/os_templates?page={number}&page_size={number}
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
        "active": 1,
        "label": "CentOS-7.2",
        "id": 1,
        "name": "centos72_multi-user_2016-09-15_128G.qcow2",
        "os_init_id": 3
    },{
        "more" : "more"
    }],
    "paging": {
        "prev": "http://127.0.0.1:8008/api/os_templates?page=1&page_size=50&filter=&order=asc&order_by=id",
        "last": "http://127.0.0.1:8008/api/os_templates?page=1&page_size=50&filter=&order=asc&order_by=id",
        "page_size": 50,
        "next": "http://127.0.0.1:8008/api/os_templates?page=1&page_size=50&filter=&order=asc&order_by=id",
        "limit": 50,
        "offset": 0,
        "total": 1,
        "page": 1,
        "first": "http://127.0.0.1:8008/api/os_templates?page=1&page_size=50&filter=&order=asc&order_by=id"
    }
}
```

| 参数名称    | 必须 |  类型   | 说明              |
|:-----------|:---:|:-------:|:------------------|
| id         |  Y  |  Long   | 模板 ID           |
| label      |  Y  | String  | 标识              |
| name       |  Y  | String  | 路径中的模板名称    |
| active     |  Y  | Boolean | 是否可用           |
| os_init_id |  N  |  Long   | 实例初始化操作簇 ID |


## 更改系统模板信息

> 更改指定 id 的系统模板信息

```http
PATCH https://$domain
  /api/os_template/{id}
Body:
{
    "label": 'CentOS-72'
}
```

可用的更新系统模板信息字段描述参见 [获取系统模板列表](#获取系统模板列表)

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": {
        "active": 1,
        "label": "CentOS-72",
        "id": 1,
        "name": "centos72_multi-user_2016-09-15_128G.qcow2",
        "os_init_id": 3
    }
}
```

系统模板信息字段描述参见 [获取系统模板列表](#获取系统模板列表)


## 删除系统模板

> 删除指定 id 的系统模板

```http
DELETE https://$domain
  /api/os_template/{id}
```

| 参数名称 | 必须 |  类型  | 说明       |
|:--------|:---:|:------:|:-----------|
| id      |  Y  | Number | 系统模板 ID |

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

