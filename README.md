[![License](https://img.shields.io/badge/License-GPL3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0.html)
[![Format](https://img.shields.io/badge/Format-JSON-blue.svg)](http://www.json.org/json-zh.html)
[![Python versions](https://img.shields.io/badge/Python-2.7.10-blue.svg)](https://www.python.org)
[![API](https://img.shields.io/badge/API-RESTful-blue.svg)](http://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)


[TOC]: # "目录"

# 目录
- [项目描述](#项目描述)
- [功能指标](#功能指标)
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
    - [[配置](docs/config.md)](#配置)
    - [[实例初始化操作簇](docs/boot_job.md)](#实例初始化操作簇)
    - [[系统模板](docs/os_template.md)](#系统模板)
    - [[Guest](docs/guest.md)](#guest)
    - [[磁盘](docs/disk.md)](#磁盘)
- [流程图](#流程图)
- [Web端](#web端)
- [问题反馈](#问题反馈)
- [项目成员](#项目成员)
- [Web端程序截图](#web端程序截图)
- [Demo](#demo)


## 项目描述

> 计算机硬件越来越白菜价，性能越来越强劲，企业电子信息化方面的业务越来越多，"互联网+"、大数据的浪潮已经掀起，物联网、AI的趋势正在形成。
> 因为上述的一切，虚拟化技术被处于一个软化硬件，揉和硬件与业务系统这么一个核心角色。
> 虚拟化技术虽然已经被普及了很久，但多数企业依然仅仅是把它当做独立的虚拟硬件来使用。在资源的科学分配、高效利用、自动化管理方面，还差那么几步。
> JimV 是一个，结构清晰简单，易于部署、维护、使用的，低门槛企业私有云管理平台。相比于业界知名的 OpenStack、OpenNebula...，JimV 不需要庞大的维护团队。


## 功能指标
|功能|JimV|
|:-|:-:|
|部署复杂度|低|
|维护复杂度|低|
|KVM虚拟化|✓|
|本地存储|✓|
|共享挂载点|✓|
|GlusterFS|✓|
|Windows Guest|✓|
|Linux Guest|✓|
|Guest 性能统计|✓|
|计算节点性能统计|✓|
|CPU超分|✓|
|内存超分|✓|
|磁盘超配|✓|
|云盘管理|✓|
|云盘热挂载|✓|
|热迁移|✓|
|批量创建|✓|
|RESTful 风格的 API|✓|
|Virtio设备|✓|
|Guest 暂停/恢复|✓|


## 未来计划

>* 增加计费功能
>* 增加 Guest 变配功能
>* 增加过期 Guest 自动回收机制
>* 增加模板上传功能
>* 增加磁盘IO限额管理功能
>* 增加磁盘吞吐量限额管理功能
>* 增加网络流量限额管理功能
>* 增加 tag 功能
>* 增加替换 IP 功能
>* 多租户
>* 用户操作轨迹
>* 用户管理功能
>* 参照gitlab，打包出 CentOS yum 一语安装仓库
>* 支持快照
>* 支持在线镜像商城
>* 国际化
>* SSH 公钥管理、注入功能
>* 加入移动端的支持


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
mysql -u jimv -pyour_jimv_db_password < ~/sites/JimV-C/misc/init.sql
# 确认是否初始化成功
mysql -u jimv -pyour_jimv_db_password -e 'show databases'
```

### 修改配置文件

配置文件的默认读取路径：`/etc/jimvc.conf`
``` bash
sudo cp ~/sites/JimV-C/jimvc.conf /etc/jimvc.conf
```
**提示：**
> 下表中凸显的配置项，需要用户根据自己的环境手动修改。

| 配置项             | 默认值                   | 说明              |
|:------------------|:------------------------|:-----------------|
| listen            | 127.0.0.1               | JimV-C 侦听的地址 |
| port              | 8008                    | JimV-C 侦听的端口 |
| db_name           | jimv                    | 数据库名称        |
| db_host           | localhost               | 数据库地址        |
| db_port           | 3306                    | 数据库端口        |
| db_user           | jimv                    | 连接数控的用户名   |
| **`db_password`** | jimv.pswd.com           | 连接数控的密码     |
| redis_host        | localhost               | redis数据库地址   |
| redis_port        | 2501                    | redis数据库端口   |
| **`redis_password`**                       || redis数据库密码   |
| redis_dbid        | 0                       | 连接的redis数据库  |
| log_file_path     | /var/log/jimv/jimvc.log | 日志存储路径       |
| **`jwt_secret`**                           || token安全码       |
| **`SECRET_KEY`**  |                         | session安全码     |
| **`smtp_host`**                            || SMTP 服务器地址   |
| smtp_port         | 25                      | SMTP 服务器端口   |
| **`smtp_user`**                            || SMTP 用户         |
| **`smtp_password`**                        || SMTP 密码         |
| smtp_starttls     | true                    | SMTP 是否开启 TLS |


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

        root /home/www/sites/JimV-C;

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
            proxy_pass         http://127.0.0.1:8008;
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

### [配置](docs/config.md)

### [实例初始化操作簇](docs/boot_job.md)

### [系统模板](docs/os_template.md)

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
