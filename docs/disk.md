# Disk

[TOC]: # "目录"

# 目录
- [创建磁盘](#创建磁盘)
- [磁盘扩容](#磁盘扩容)
- [获取磁盘信息](#获取磁盘信息)
- [更新磁盘信息](#更新磁盘信息)
- [获取磁盘列表](#获取磁盘列表)
- [磁盘全文检索](#磁盘全文检索)
- [删除磁盘](#删除磁盘)


## 创建磁盘

> 创建磁盘

```http
POST https://$domain
  /api/disk
Body:
{
    "size": 4
}
```

| 参数名称 | 必须 | 类型 | 说明             |
|:-------:|:---:|:----:|:-----------------|
|  size   |  Y  | Long | 磁盘大小，单位`GB` |

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


## 磁盘扩容

> 磁盘扩容

```http
PUT https://$domain
  /api/disk/_disk_resize/{uuid}/{size}
```

| 参数名称 | 必须 |  类型  | 说明            |
|:-------:|:---:|:------:|:----------------|
|  uuid   |  Y  | String | 磁盘的uuid       |
|  size   |  Y  |  Long  | 扩容至，单位`GB` |

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


## 获取磁盘信息

> 获取指定 UUID 的磁盘信息

```http
GET https://$domain
  /api/disk/{uuid}
```

| 参数名称 | 必须 |  类型  | 说明            |
|:-------:|:---:|:------:|:----------------|
|  uuid   |  Y  | String | 磁盘的uuid       |

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": {
        "guest_uuid": "",
        "uuid": "fff8aead-3206-4820-8c98-146178a91cce",
        "sequence": -1,
        "format": "qcow2",
        "label": "Hello-disk",
        "state": 1,
        "id": 42,
        "size": 200
    }
}
```

| 参数名称    | 必须 |  类型  | 说明                                                  |
|:-----------|:---:|:------:|:------------------------------------------------------|
| id         |  Y  |  Long  | 磁盘 ID                                               |
| uuid       |  Y  | String | 磁盘 UUID                                             |
| label      |  Y  | String | 磁盘标注信息                                           |
| size       |  Y  |  Long  | 磁盘大小                                               |
| sequence   |  Y  |  Long  | 磁盘在某个 Guest 实例中的序列                            |
| format     |  Y  | String | 磁盘镜像格式，默认 qcow2                                |
| state      |  Y  |  Long  | 磁盘当前状态，可用状态值请参考 [磁盘状态](enum.md#磁盘状态) |
| guest_uuid |  Y  | String | 当前磁盘被使用的 Guest 实例                             |


## 更新磁盘信息

> 更改指定 uuid 的磁盘信息

```http
PATCH https://$domain
  /api/disk/{uuid}
Body:
{
    "label": "desc"
}
```

| 参数名称 | 必须 |  类型  | 说明 |
|:--------|:---:|:------:|:-----|
| label   |  Y  | String | 标注 |

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": {
        "guest_uuid": "",
        "uuid": "fff8aead-3206-4820-8c98-146178a91cce",
        "format": "qcow2",
        "sequence": -1,
        "label": "Hello-disk",
        "state": 0,
        "id": 42,
        "size": 10
    }
}
```

磁盘信息字段描述参见 [获取磁盘信息](#获取磁盘信息)


## 获取磁盘列表

> 获取磁盘列表

```http
GET https://$domain
  /api/disks?offset={number}&limit={number}
  or
  /api/disks?page={number}&page_size={number}
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
        "guest_uuid": "",
        "uuid": "5844e2cb-56c5-4b02-98b5-ee606bfbe3b3",
        "sequence": -1,
        "format": "qcow2",
        "label": "82QUZJGJ",
        "state": 0,
        "id": 22,
        "size": 10
    }, {
       "more": "more"
    }, {
        "guest_uuid": "",
        "uuid": "fff8aead-3206-4820-8c98-146178a91cce",
        "sequence": -1,
        "format": "qcow2",
        "label": "qhDCp3E8",
        "state": 0,
        "id": 42,
        "size": 10
    }],
    "paging": {
        "prev": "http://127.0.0.1:8008/api/disks?page=1&page_size=50&filter=&order=asc&order_by=id",
        "last": "http://127.0.0.1:8008/api/disks?page=1&page_size=50&filter=&order=asc&order_by=id",
        "page_size": 50,
        "next": "http://127.0.0.1:8008/api/disks?page=1&page_size=50&filter=&order=asc&order_by=id",
        "limit": 50,
        "offset": 0,
        "total": 10,
        "page": 1,
        "first": "http://127.0.0.1:8008/api/disks?page=1&page_size=50&filter=&order=asc&order_by=id"
    }
}
```

| 参数名称   | 必须 |  类型  | 说明                                            |
|:----------|:---:|:------:|:------------------------------------------------|
| total     |  Y  | Number | 用户总量                                         |
| offset    |  Y  | Number | 当前偏移量                                       |
| limit     |  Y  | Number | 返回条目数量                                     |
| page      |  Y  | Number | 透传客户端请求的该参数, 如果没有传递, 则返回默认值1   |
| page_size |  Y  | Number | 透传客户端请求的该参数, 如果没有传递, 则返回默认值 50 |

磁盘信息字段描述参见 [获取磁盘信息](#获取磁盘信息)


## 磁盘全文检索

> 根据关键字查找磁盘信息

```http
GET https://$domain
  /api/disks/_search?offset={number}&limit={number}&keyword=hello
  or
  /api/disks/_search?page={number}&page_size={number}&keyword=hello
```

| 参数名称   | 必须 |  类型  | 说明                                        |
|:----------|:---:|:------:|:--------------------------------------------|
| offset    |  N  | Number | 偏移量, 默认值0                              |
| limit     |  N  | Number | 返回条目数量, 默认值50                        |
| page      |  N  | Number | 页号, 与offset同时存在时, 以offset为准, 默认值1 |
| page_size |  N  | Number | 页大小, 默认值50                             |
| order_by  |  N  | String | 所依据的字段                                 |
| order     |  N  |  Enum  | 排序策略，`asc`\|`desc`                      |
| keyword   |  N  | String | 全文检索的关键字                              |

响应示例

```json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": [{
        "guest_uuid": "",
        "uuid": "fff8aead-3206-4820-8c98-146178a91cce",
        "sequence": -1,
        "format": "qcow2",
        "label": "Hello-disk",
        "state": 1,
        "id": 42,
        "size": 200
    }],
    "paging": {
        "prev": "http://127.0.0.1:8008/api/disks/_search?page=1&page_size=50&keyword=hello&order=asc&order_by=id",
        "last": "http://127.0.0.1:8008/api/disks/_search?page=1&page_size=50&keyword=hello&order=asc&order_by=id",
        "page_size": 50,
        "next": "http://127.0.0.1:8008/api/disks/_search?page=1&page_size=50&keyword=hello&order=asc&order_by=id",
        "limit": 50,
        "offset": 0,
        "total": 1,
        "page": 1,
        "first": "http://127.0.0.1:8008/api/disks/_search?page=1&page_size=50&keyword=hello&order=asc&order_by=id"
    }
}
```

| 参数名称   | 必须 |  类型  | 说明                                            |
|:----------|:---:|:------:|:------------------------------------------------|
| total     |  Y  | Number | 用户总量                                         |
| offset    |  Y  | Number | 当前偏移量                                       |
| limit     |  Y  | Number | 返回条目数量                                     |
| page      |  Y  | Number | 透传客户端请求的该参数, 如果没有传递, 则返回默认值1   |
| page_size |  Y  | Number | 透传客户端请求的该参数, 如果没有传递, 则返回默认值 50 |

磁盘信息字段描述参见 [获取磁盘信息](#获取磁盘信息)


## 删除磁盘

> 删除指定 uuid 的磁盘

```http
DELETE https://$domain
  /api/disks/{uuids}
```

| 参数名称 | 必须 |  类型  | 说明                                           |
|:--------|:---:|:------:|:-----------------------------------------------|
| uuids   |  Y  | String | uuids可为多个或单个uuid。多个磁盘的uuid以逗号间隔。 |

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