[![License](https://img.shields.io/badge/License-GPL3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0.html)
[![Format](https://img.shields.io/badge/Format-JSON-blue.svg)](http://www.json.org/json-zh.html)
[![Python versions](https://img.shields.io/badge/Python-2.7.10-blue.svg)](https://www.python.org)
[![API](https://img.shields.io/badge/API-RESTful-blue.svg)](http://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)


[TOC]: # "目录"

# 目录
- [项目描述](#项目描述)
- [未来计划](#未来计划)
- [安装](#安装)
    - [创建web用户](#创建web用户)
    - [创建站点发布目录](#创建站点发布目录)
    - [克隆JimV-C项目](#克隆jimv-c项目)
    - [安装所需库](#安装所需库)
    - [初始化JimV MySQL数据库](#初始化jimv-mysql数据库)
    - [修改配置文件](#修改配置文件)
    - [启动服务](#启动服务)
    - [Nginx 参考配置](#nginx-参考配置)
- [API](#api)
    - [[状态码参考列表](docs/state_code.md)](#状态码参考列表)
    - [[过滤器操作符原语](docs/filter_primitive.md)](#过滤器操作符原语)
    - [[状态列表](docs/enum.md)](#状态列表)
    - [[Guest](docs/guest.md)](#guest)
    - [[磁盘](docs/disk.md)](#磁盘)
- [流程图](#流程图)
- [Web端](#web端)
- [问题反馈](#问题反馈)
- [项目成员](#项目成员)
- [Web端程序截图](#web端程序截图)
- [Demo](#demo)


## 项目描述

> JimV-C 是 JimV 的控制节点。JimV 是一个轻量级的 KVM 虚拟化环境管理平台。
> * 纯 HTTP 的交互方式；


## 未来计划

>* 增加计费功能
>* 增加过期资源自动回收机制
>* 增加模板上传功能
>* 日志处理机制
>* 用户管理功能
>* 参照gitlab，打包出 CentOS yum 一语安装仓库
>* 加入移动端的支持；


## 安装

### 创建web用户

```bash
useradd -m www
```

### 创建站点发布目录

```bash
su - www
mkdir ~/sites
```

### 克隆JimV-C项目

```bash
git clone https://github.com/jamesiter/JimV-C.git ~/sites/JimV-C
```

### 安装所需库

```bash
# 创建 python 虚拟环境
virtualenv --system-site-packages venv
# 导入 python 虚拟环境
source ~/venv/bin/activate
# 安装JimV-C所需扩展库
pip install -r ~/sites/JimV-C/requirements.txt
# 安装Python连接MySQL的适配器
git clone https://github.com/mysql/mysql-connector-python.git; cd ~/mysql-connector-python; python setup.py install; cd ..; rm -rf mysql-connector-python
```

### 初始化JimV MySQL数据库

```bash
# 建立 JimV 数据库专属用户
mysql -u root -pyour_db_password -e 'grant all on jimv.* to jimv@localhost identified by "your_jimv_db_password"; flush privileges'
# 初始化数据库
mysql -u jimv -pyour_jimv_db_password < sites/jimv/misc/init.sql
# 确认是否初始化成功
mysql -u jimv -pyour_jimv_db_password -e 'show databases'
```

### 修改配置文件

配置文件路径：`sites/JimV-C/config.json` <br> **提示：**
> 下表中凸显的配置项，需要用户根据自己的环境手动修改。

| 配置项                      | 默认值                | 说明                                          |
|:---------------------------|:---------------------|:---------------------------------------------|
| db_name                    | jimv                 | 数据库名称                                    |
| db_host                    | localhost            | 数据库地址                                    |
| db_port                    | 3306                 | 数据库端口                                    |
| db_user                    | jimv                 | 连接数控的用户名                               |
| **`db_password`**          | jimv.pswd.com        | 连接数控的密码                                 |
| db_pool_size               | 10                   | 连接池                                        |
| db_charset                 | utf8                 | 默认字符集                                    |
| redis_host                 | localhost            | redis数据库地址                               |
| redis_port                 | 2501                 | redis数据库端口                               |
| **`redis_password`**                             || redis数据库密码                               |
| redis_dbid                 | 0                    | 连接的redis数据库                              |
| debug                      | false                | 是否为调试模式                                 |
| log_cycle                  | D                    | 日志轮转周期                                   |
| token_ttl                  | 604800               | token有效期                                   |
| **`jwt_secret`**                                 || token安全码                                   |
| jwt_algorithm              | HS512                | token哈希算法                                 |
| SESSION_TYPE               | filesystem           | session存放类型                               |
| SESSION_PERMANENT          | true                 | session是否持久化存储                          |
| SESSION_USE_SIGNER         | true                 | session是否使用并校验签名                       |
| SESSION_FILE_DIR           | ../cache             | session存放路径                               |
| SESSION_FILE_THRESHOLD     | 1000                 | 存放的session超过该数量，之前的将被删除           |
| SESSION_COOKIE_NAME        | sid                  | session id在客户端cookie中的存放名称            |
| SESSION_COOKIE_SECURE      | false                | cookie的传输是否只在https的环境中进行            |
| **`SECRET_KEY`**           |                      | session安全码                                 |
| PERMANENT_SESSION_LIFETIME | 604800               | cookie在客户端的持久化时间。该值需与token_ttl相同 |
| vm_create_queue            | Q:VMCreate           | 创建虚拟机的队列                               |
| host_event_report_queue    | Q:HostEvent          | 宿主机事件上抛队列                              |
| ip_available_set           | S\:IP:Available      | 虚拟化环境中可用 IP 集合                        |
| ip_used_set                | S\:IP:Used           | 虚拟化环境中已用 IP 地址集合                    |
| vnc_port_available_set     | S\:VNCPort:Available | 虚拟化环境中可用 VNC 端口集合                   |
| vnc_port_used_set          | S\:VNCPort:Used      | 虚拟化环境中已用 VNC 端口集合                   |

### 启动服务

```bash
# 进入JimV-C目录
cd ~/sites/JimV-C
# 启动JimV-C
gunicorn -c gunicorn_config.py main:app
```

### Nginx 参考配置

```nginx
    gzip on;
    gzip_min_length 1100;
    gzip_buffers 4 8k;
    gzip_types text/plain application/javascript text/css;

    autoindex off;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options: nosniff;

    server {
        listen 443;
        server_name jimv.your-domain;

        access_log  /var/log/nginx/jimv.access.log;
        error_log  /var/log/nginx/jimv.error.log;

        ssl on;
        ssl_certificate /opt/pki/tls/certs/jimv.your.crt;
        ssl_certificate_key /opt/pki/tls/certs/jimv.your.key;
        ssl_session_timeout 5m;
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers AESGCM:ALL:!DH:!EXPORT:!RC4:+HIGH:!MEDIUM:!LOW:!aNULL:!eNULL;
        ssl_prefer_server_ciphers on;

        root /home/www/sites/jimv/html;

        # 拒绝访问隐藏文件(如：.git、.svn等目录)
        location ~ /\..* {
            return 403;
        }
        location ~ .(sql|py|pyc|ini|conf|log|svn|git|cfg)$ {
            return 403;
        }
        location ~ /$ {
            rewrite http://$host/index.html break;
        }
        location / {
            try_files $uri @inner;
        }

        location @inner {
            proxy_pass         http://127.0.0.1:8001;
            proxy_redirect     off;
            proxy_set_header   Host             $host;
            proxy_set_header   X-Real-IP        $remote_addr;
            proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
        }
    }
```


## API

> 默认数据交互格式 Content-Type: application/json

### [状态码参考列表](docs/state_code.md)

### [过滤器操作符原语](docs/filter_primitive.md)

### [状态列表](docs/enum.md)

### [Guest](docs/guest.md)

### [磁盘](docs/disk.md)



## 流程图


## Web端

[Web端项目地址](https://github.com/jamesiter/JimV-C-web)


## 问题反馈

[提交Bug](https://github.com/jamesiter/JimV-C/issues) <br> 技术交流 QQ 群:
377907881


## 项目成员

<pre>
姓名:    James Iter
E-Mail: james.iter.cn@gmail.com
</pre>


## Web端程序截图

[Web端程序截图](docs/screenshot.md)


## Demo

[demo.jimv.org](https://demo.jimv.org) <br> 管理员账密 `admin`:`admin`
