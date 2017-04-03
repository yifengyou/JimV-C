# 过滤器操作符原语

## 原语说明
|操作符原语|示例|说明|
|:--|:--|:--|
|eq|id:eq:5|过滤出`id`字段`等于` `5`的条目。|
|gt|create_time:gt:1487236163783548|过滤出时间戳字段`create_time` `大于` `1487236163783548`的条目。|
|lt|create_time:gt:1487246163783548|过滤出时间戳字段`create_time` `小于` `1487246163783548`的条目。|
|ne|role_id:ne:0|过滤出角色字段`role_id` `不等于` `1`的条目。|
|in|id:in:6o3H13DqJOiTu53v,UuAsvSbVTsyHpqvF|过滤出应用id字段`id` `为` `6o3H13DqJOiTu53v`或`UuAsvSbVTsyHpqvF`的条目。|
|notin|id:notin:6o3H13DqJOiTu53v,UuAsvSbVTsyHpqvF|过滤出应用id字段`id` `不为` `6o3H13DqJOiTu53v`且`UuAsvSbVTsyHpqvF`的条目。|
|like|mobile_phone:like:156|过滤出用户手机号码字段`mobile_phone` `包含` `156`的条目。|
|\:|id:eq:5|过滤语句中，主、谓、宾的分隔符。|
|,|id:in:6o3H13DqJOiTu53v,UuAsvSbVTsyHpqvF|一个过滤语句中，多个值之间的分隔符。|
|;|mobile_phone:like:156;create_time:gt:1487054296057012|多个过滤语句间的分隔符。|


## 组合操作示例
> 过滤出用户手机号码包含156，且创建时间大于1487054296057012的用户。

``` http
GET http://jimauth.dev.iit.im
  /api/users_mgmt?filter=mobile_phone:like:156;create_time:gt:1487054296057012
```

响应示例
``` json
{
    "state": {
        "code": "200",
        "zh-cn": "成功",
        "en-us": "OK"
    },
    "data": [{
        "mobile_phone": "15600000000",
        "login_name": "mm5h5pao3r",
        "mobile_phone_verified": 0,
        "email_verified": 0,
        "enabled": 1,
        "id": 373,
        "role_id": 0,
        "manager": 0,
        "create_time": 1487140251278993,
        "email": ""
    }, {
        "mobile_phone": "15600000010",
        "login_name": "uz6hp2hd5x",
        "mobile_phone_verified": 0,
        "email_verified": 0,
        "enabled": 1,
        "id": 376,
        "role_id": 0,
        "manager": 0,
        "create_time": 1487140279849145,
        "email": ""
    }],
    "paging": {
        "first": "http://jimauth.dev.iit.im/api/users_mgmt?page=1&page_size=50&filter=mobile_phone:like:156;create_time:gt:1487054296057012&order=asc&order_by=id",
        "prev": "http://jimauth.dev.iit.im/api/users_mgmt?page=1&page_size=50&filter=mobile_phone:like:156;create_time:gt:1487054296057012&order=asc&order_by=id",
        "limit": 50,
        "offset": 0,
        "last": "http://jimauth.dev.iit.im/api/users_mgmt?page=1&page_size=50&filter=mobile_phone:like:156;create_time:gt:1487054296057012&order=asc&order_by=id",
        "total": 2,
        "page": 1,
        "page_size": 50,
        "next": "http://jimauth.dev.iit.im/api/users_mgmt?page=1&page_size=50&filter=mobile_phone:like:156;create_time:gt:1487054296057012&order=asc&order_by=id"
    }
}
```


**`提示`**
<br>
**in** 包含 `等于` 及 `或等于` 的意思；
<br>
**not in** 包含 `不等于` 及 `且不等于` 的意思。
