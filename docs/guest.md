# Guest


## 创建 Guest
> 创建 Guest

``` http
POST https://$domain
  /api/guest
Body:
{
    "cpu": 4,
    "memory": 4,
    "os_template_id": 1,
    "quantity": 1,
    "name": "",
    "password": "pswd.com",
    "lease_term": 100
}
```

|参数名称|必须|类型|说明|
|:--:|:--:|:--:|:--:|
|cpu|Y|Long|CPU 个数|
|memory|Y|Long|内存大小，单位`MB`|
|os_template_id|Y|Long|模板ID|
|quantity|Y|Long|本次创建的，同样配置的实例数量|
|name|N|String|实例名称。如果quantity大于1，则会在实例名称后面追加`-序号`，组成新的实例名称。如果实例名称为空字符串时，实例名称将为8位的随机字符串。|
|password|N|String|实例管理员用户密码。为空字符串时，密码将为16位的随机字符串。|
|lease_term|Y|Long|租期。过期后，实例将被置于悬挂状态，并在一周后自动删除。单位`到期的时间戳`。|


## 获取 Guest 信息
> 获取指定 UUID 的 Guest 信息

``` http
GET https://$domain
  /api/guest/{uuid}
```

响应示例
``` json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": {
        "status": 1,
        "xml": "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n            <domain type=\"kvm\">\n            \n            <features>\n                <acpi/>\n                <apic/>\n            </features>\n        \n            <name>4hd3Dop4</name>\n            <uuid>01ee4d15-7165-4859-b8d4-d2c3c0ea22c3</uuid>\n            <vcpu>4</vcpu>\n            <memory unit=\"GiB\">4</memory>\n            \n            <os>\n                <boot dev=\"hd\"/>\n                <type arch=\"x86_64\">hvm</type>\n                <bootmenu timeout=\"3000\" enable=\"yes\"/>\n            </os>\n        \n            \n            <devices>\n                \n            <interface type='network'>\n                <source network='net-br0'/>\n                <model type='virtio'/>\n            </interface>\n        \n                \n                <disk type='network' device='disk'>\n                    <driver name='qemu' type='qcow2' cache='none'/>\n                    <source protocol='gluster' name='gv0/VMs/4hd3Dop4/f0f76139-d909-4270-a9fa-678b34aa01f7.qcow2'>\n                        <host name='127.0.0.1' port='24007'/>\n                    </source>\n                    <target dev='vda' bus='virtio'/>\n                </disk>\n        \n                \n            <graphics passwd=\"eg9nEWNanoPMBdFz\" keymap=\"en-us\" port=\"16004\" type=\"vnc\">\n                <listen network=\"net-br0\" type=\"network\"/>\n            </graphics>\n        \n                \n            <serial type='pty'>\n                <target port='0'/>\n            </serial>\n            <console type='pty'>\n                <target type='serial' port='0'/>\n            </console>\n        \n            </devices>\n        \n            </domain>\n        ",
        "remark": "zabbix",
        "vnc_password": "eg9nEWNanoPMBdFz",
        "name": "4hd3Dop4",
        "os_template_id": 1,
        "ip": "10.10.6.78",
        "vnc_port": 16004,
        "id": 19,
        "network": "net-br0",
        "create_time": 1495005882742821,
        "manage_network": "net-br0",
        "memory": 4,
        "on_host": "10k01.jkser.com",
        "password": "pswd.com",
        "cpu": 4,
        "uuid": "01ee4d15-7165-4859-b8d4-d2c3c0ea22c3"
    }
}
```
|参数名称|必须|类型|说明|
|:--|:--:|:--:|:--|
|id|Y|Long|Guest ID|
|uuid|Y|String|Guest UUID|
|name|Y|String|实例名称|
|password|Y|String|Guest 密码|
|remark|Y|String|实例备注|
|os_template_id|Y|Long|实例被衍生出来的模板 ID|
|create_time|Y|Long|创建时间，单位`微秒`|
|status|Y|Long|Guest 当前的运行状态。可用状态值请参考 [Guest 状态](enum.md#guest-状态)|
|on_host|Y|String|实例所在的宿主机|
|cpu|Y|Long|CPU 个数|
|memory|Y|Long|内存大小，单位`GB`|
|ip|Y|String|实例的 IP 地址|
|network|Y|String|实例所在的 业务网络|
|manage_network|Y|String|实例所在的 管理网络|
|vnc_port|Y|Long|连接实例的 VNC 端口|
|vnc_password|Y|String|连接实例的 VNC 密码|
|xml|Y|String|创建实例时的 xml 描述文档|


## 获取 Guest 列表
> 获取 Guest 列表

``` http
GET https://$domain
  /api/guests?offset={number}&limit={number}
  or
  /api/guests?page={number}&page_size={number}
```

|参数名称|必须|类型|说明|
|:--:|:--:|:--:|:--:|
|offset|N|Number|偏移量, 默认值0|
|limit|N|Number|返回条目数量, 默认值50|
|page|N|Number|页号, 与offset同时存在时, 以offset为准, 默认值1|
|page_size|N|Number|页大小, 默认值50|
|order_by|N|String|所依据的字段|
|order|N|Enum|排序策略，`asc`\|`desc`|

响应示例
``` json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": [{
        "status": 1,
        "xml": "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n            <domain type=\"kvm\">\n            \n            <features>\n                <acpi/>\n                <apic/>\n            </features>\n        \n            <name>rlqM4Gvv</name>\n            <uuid>60e4b9a2-11c8-44ed-82ca-28740ee81ade</uuid>\n            <vcpu>4</vcpu>\n            <memory unit=\"GiB\">4</memory>\n            \n            <os>\n                <boot dev=\"hd\"/>\n                <type arch=\"x86_64\">hvm</type>\n                <bootmenu timeout=\"3000\" enable=\"yes\"/>\n            </os>\n        \n            \n            <devices>\n                \n            <interface type='network'>\n                <source network='net-br0'/>\n                <model type='virtio'/>\n            </interface>\n        \n                \n                <disk type='network' device='disk'>\n                    <driver name='qemu' type='qcow2' cache='none'/>\n                    <source protocol='gluster' name='gv0/VMs/rlqM4Gvv/954b7d47-0dad-4e8d-9e31-a0d01f3b3bf6.qcow2'>\n                        <host name='127.0.0.1' port='24007'/>\n                    </source>\n                    <target dev='vda' bus='virtio'/>\n                </disk>\n        \n                \n            <graphics passwd=\"4pJDvweOtR0ayRfG\" keymap=\"en-us\" port=\"16104\" type=\"vnc\">\n                <listen network=\"net-br0\" type=\"network\"/>\n            </graphics>\n        \n                \n            <serial type='pty'>\n                <target port='0'/>\n            </serial>\n            <console type='pty'>\n                <target type='serial' port='0'/>\n            </console>\n        \n            </devices>\n        \n            </domain>\n        ",
        "remark": "zabbix",
        "name": "rlqM4Gvv",
        "os_template_id": 1,
        "ip": "10.10.5.1",
        "vnc_port": 16104,
        "uuid": "60e4b9a2-11c8-44ed-82ca-28740ee81ade",
        "cpu": 4,
        "create_time": 1494247162181399,
        "manage_network": "net-br0",
        "memory": 4,
        "id": 12,
        "password": "pswd.com",
        "on_host": "10k01.jkser.com",
        "vnc_password": "4pJDvweOtR0ayRfG",
        "network": "net-br0"
    }, {
          ...
    }, {
        "status": 0,
        "xml": "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n            <domain type=\"kvm\">\n            \n            <features>\n                <acpi/>\n                <apic/>\n            </features>\n        \n            <name>4hd3Dop4</name>\n            <uuid>01ee4d15-7165-4859-b8d4-d2c3c0ea22c3</uuid>\n            <vcpu>4</vcpu>\n            <memory unit=\"GiB\">4</memory>\n            \n            <os>\n                <boot dev=\"hd\"/>\n                <type arch=\"x86_64\">hvm</type>\n                <bootmenu timeout=\"3000\" enable=\"yes\"/>\n            </os>\n        \n            \n            <devices>\n                \n            <interface type='network'>\n                <source network='net-br0'/>\n                <model type='virtio'/>\n            </interface>\n        \n                \n                <disk type='network' device='disk'>\n                    <driver name='qemu' type='qcow2' cache='none'/>\n                    <source protocol='gluster' name='gv0/VMs/4hd3Dop4/f0f76139-d909-4270-a9fa-678b34aa01f7.qcow2'>\n                        <host name='127.0.0.1' port='24007'/>\n                    </source>\n                    <target dev='vda' bus='virtio'/>\n                </disk>\n        \n                \n            <graphics passwd=\"eg9nEWNanoPMBdFz\" keymap=\"en-us\" port=\"16004\" type=\"vnc\">\n                <listen network=\"net-br0\" type=\"network\"/>\n            </graphics>\n        \n                \n            <serial type='pty'>\n                <target port='0'/>\n            </serial>\n            <console type='pty'>\n                <target type='serial' port='0'/>\n            </console>\n        \n            </devices>\n        \n            </domain>\n        ",
        "remark": "",
        "name": "4hd3Dop4",
        "os_template_id": 1,
        "ip": "10.10.6.78",
        "vnc_port": 16004,
        "uuid": "01ee4d15-7165-4859-b8d4-d2c3c0ea22c3",
        "cpu": 4,
        "create_time": 1495005882742821,
        "manage_network": "net-br0",
        "memory": 4,
        "id": 19,
        "password": "pswd.com",
        "on_host": "",
        "vnc_password": "eg9nEWNanoPMBdFz",
        "network": "net-br0"
    }],
    "paging": {
        "prev": "http://127.0.0.1:8008/api/guests?page=1&page_size=50&filter=&order=asc&order_by=id",
        "last": "http://127.0.0.1:8008/api/guests?page=1&page_size=50&filter=&order=asc&order_by=id",
        "page_size": 50,
        "next": "http://127.0.0.1:8008/api/guests?page=1&page_size=50&filter=&order=asc&order_by=id",
        "limit": 50,
        "offset": 0,
        "total": 8,
        "page": 1,
        "first": "http://127.0.0.1:8008/api/guests?page=1&page_size=50&filter=&order=asc&order_by=id"
    }
}
```

|参数名称|必须|类型|说明|
|:--|:--:|:--:|:--|
|total|Y|Number|用户总量|
|offset|Y|Number|当前偏移量|
|limit|Y|Number|返回条目数量|
|page|Y|Number|透传客户端请求的该参数, 如果没有传递, 则返回默认值1|
|page_size|Y|Number|透传客户端请求的该参数, 如果没有传递, 则返回默认值 50|

Guest 信息字段描述参见 [获取 Guest 信息](guest.md#获取-guest-信息)


## 更改 Guest 信息
> 更改指定 uuid 的 Guest 信息

``` http
PATCH https://$domain
  /api/guest/{uuid}
Body:
{
    "remark": "desc"
}
```

|参数名称|必须|类型|说明|
|:--|:--:|:--:|:--|
|remark|N|String|备注|

响应示例
``` json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    },
    "data": {
        "status": 1,
        "xml": "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n            <domain type=\"kvm\">\n            \n            <features>\n                <acpi/>\n                <apic/>\n            </features>\n        \n            <name>4hd3Dop4</name>\n            <uuid>01ee4d15-7165-4859-b8d4-d2c3c0ea22c3</uuid>\n            <vcpu>4</vcpu>\n            <memory unit=\"GiB\">4</memory>\n            \n            <os>\n                <boot dev=\"hd\"/>\n                <type arch=\"x86_64\">hvm</type>\n                <bootmenu timeout=\"3000\" enable=\"yes\"/>\n            </os>\n        \n            \n            <devices>\n                \n            <interface type='network'>\n                <source network='net-br0'/>\n                <model type='virtio'/>\n            </interface>\n        \n                \n                <disk type='network' device='disk'>\n                    <driver name='qemu' type='qcow2' cache='none'/>\n                    <source protocol='gluster' name='gv0/VMs/4hd3Dop4/f0f76139-d909-4270-a9fa-678b34aa01f7.qcow2'>\n                        <host name='127.0.0.1' port='24007'/>\n                    </source>\n                    <target dev='vda' bus='virtio'/>\n                </disk>\n        \n                \n            <graphics passwd=\"eg9nEWNanoPMBdFz\" keymap=\"en-us\" port=\"16004\" type=\"vnc\">\n                <listen network=\"net-br0\" type=\"network\"/>\n            </graphics>\n        \n                \n            <serial type='pty'>\n                <target port='0'/>\n            </serial>\n            <console type='pty'>\n                <target type='serial' port='0'/>\n            </console>\n        \n            </devices>\n        \n            </domain>\n        ",
        "remark": "zabbix",
        "name": "4hd3Dop4",
        "os_template_id": 1,
        "ip": "10.10.6.78",
        "vnc_port": 16004,
        "uuid": "01ee4d15-7165-4859-b8d4-d2c3c0ea22c3",
        "id": 19,
        "cpu": 4,
        "create_time": 1495005882742821,
        "manage_network": "net-br0",
        "memory": 4,
        "password": "pswd.com",
        "on_host": "10k01.jkser.com",
        "vnc_password": "eg9nEWNanoPMBdFz",
        "network": "net-br0"
    }
}
```

Guest 信息字段描述参见 [获取 Guest 信息](guest.md#获取-guest-信息)


## 重启 Guest
> 重启 Guest，uuids以逗号间隔

``` http
PUT https://$domain
  /api/guests/_reboot/{uuids}
```

|参数名称|必须|类型|说明|
|:--|:--:|:--:|:--|
|uuids|Y|String|uuids可为多个或单个uuid。多个实例的uuid以逗号间隔。|

响应示例
``` json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    }
}
```


## 关闭 Guest
> 关闭 Guest，uuids以逗号间隔

``` http
PUT https://$domain
  /api/guests/_shutdown/{uuids}
```

|参数名称|必须|类型|说明|
|:--|:--:|:--:|:--|
|uuids|Y|String|uuids可为多个或单个uuid。多个实例的uuid以逗号间隔。|

响应示例
``` json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    }
}
```


## 强制关闭 Guest
> 强制关闭 Guest，uuids以逗号间隔

``` http
PUT https://$domain
  /api/guests/_force_shutdown/{uuids}
```

|参数名称|必须|类型|说明|
|:--|:--:|:--:|:--|
|uuids|Y|String|uuids可为多个或单个uuid。多个实例的uuid以逗号间隔。|

响应示例
``` json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    }
}
```


## 启动 Guest
> 启动 Guest，uuids以逗号间隔

``` http
PUT https://$domain
  /api/guests/_boot/{uuids}
```

|参数名称|必须|类型|说明|
|:--|:--:|:--:|:--|
|uuids|Y|String|uuids可为多个或单个uuid。多个实例的uuid以逗号间隔。|

响应示例
``` json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    }
}
```


## 暂停 Guest
> 暂停 Guest，uuids以逗号间隔

``` http
PUT https://$domain
  /api/guests/_suspend/{uuids}
```

|参数名称|必须|类型|说明|
|:--|:--:|:--:|:--|
|uuids|Y|String|uuids可为多个或单个uuid。多个实例的uuid以逗号间隔。|

响应示例
``` json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    }
}
```


## 恢复 Guest
> 恢复被暂停的 Guest，uuids以逗号间隔

``` http
PUT https://$domain
  /api/guests/_resume/{uuids}
```

|参数名称|必须|类型|说明|
|:--|:--:|:--:|:--|
|uuids|Y|String|uuids可为多个或单个uuid。多个实例的uuid以逗号间隔。|

响应示例
``` json
{
    "state": {
        "en-us": "OK",
        "zh-cn": "成功",
        "code": "200"
    }
}
```


[返回上一级](../README.md)
===
