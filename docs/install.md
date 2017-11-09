# 手动安装

[TOC]: # "手动安装"

# 手动安装
- [安装必要软件](#安装必要软件)
- [部署 MariaDB](#部署-mariadb)
- [部署 Redis](#部署-redis)
- [创建 Web 用户](#创建-web-用户)
- [创建站点发布目录](#创建站点发布目录)
- [克隆JimV-C项目](#克隆jimv-c项目)
- [安装所需库](#安装所需库)
- [初始化JimV MySQL数据库](#初始化jimv-mysql数据库)
- [修改配置文件](#修改配置文件)
- [启动服务](#启动服务)
- [部署 Nginx](#部署-nginx)


## 安装必要软件

``` bash
yum install screen python2-pip -y
pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
pip install virtualenv -i https://mirrors.aliyun.com/pypi/simple/
```

## 部署 MariaDB
``` bash
# 安装 MariaDB
yum install mariadb mariadb-server -y

# 配置 MariaDB
mkdir -p /etc/systemd/system/mariadb.service.d
echo '[Service]' > /etc/systemd/system/mariadb.service.d/limits.conf
echo 'LimitNOFILE=65535' >> /etc/systemd/system/mariadb.service.d/limits.conf
systemctl --system daemon-reload

sed -i '/\[mysqld\]/a\bind-address = 127.0.0.1' /etc/my.cnf
sed -i '/\[mysqld\]/a\log-bin' /etc/my.cnf
sed -i '/\[mysqld\]/a\expire_logs_days = 1' /etc/my.cnf
sed -i '/\[mysqld\]/a\innodb_file_per_table' /etc/my.cnf
sed -i '/\[mysqld\]/a\max_connections = 1000' /etc/my.cnf

# 启动并使其随机启动
systemctl enable mariadb.service
systemctl start mariadb.service

# 初始化 MariaDB
mysql_secure_installation << EOF

Y
your_root_db_password
your_root_db_password
Y
Y
Y
Y
EOF

# 测试是否部署成功
mysql -u root -pyour_root_db_password -e 'show databases'
```

## 部署 Redis
``` bash
# 安装 Redis
yum install redis -y

# 配置 Redis
echo 'vm.overcommit_memory = 1' >> /etc/sysctl.conf
sysctl -p
sed -i '@^daemonize no@daemonize yes@g' /etc/redis.conf
sed -i 's@^bind 127.0.0.1@bind 0.0.0.0@g' /etc/redis.conf
sed -i 's@^appendonly no@appendonly yes@g' /etc/redis.conf
echo 'requirepass your_jimv_redis_passwordddddddddddddddddddddddddddddddddddddddddddddddddddddddd' >> /etc/redis.conf

# 启动并使其随机启动
systemctl enable redis.service
systemctl start redis.service
```

## 创建 Web 用户

```bash
useradd -m www
echo "www:www.pswd.com" | chpasswd
echo "www ALL = (root) ALL" >> /etc/sudoers.d/www; chmod 0440 /etc/sudoers.d/www
```

## 创建站点发布目录

```bash
su - www
mkdir ~/sites
```

## 克隆JimV-C项目

```bash
git clone https://github.com/jamesiter/JimV-C.git ~/sites/JimV-C
```

## 安装所需库

```bash
# 创建 python 虚拟环境
virtualenv --system-site-packages venv

# 导入 python 虚拟环境
source ~/venv/bin/activate

# 使切入 www 用户时自动导入 python 虚拟环境
echo '. ~/venv/bin/activate' >> .bashrc

# 安装JimV-C所需扩展库
pip install -r ~/sites/JimV-C/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

## 初始化JimV MySQL数据库

```bash
# 建立 JimV 数据库专属用户
mysql -u root -pyour_root_db_password -e 'grant all on jimv.* to jimv@localhost identified by "your_jimv_db_password"; flush privileges'
# 初始化数据库
mysql -u jimv -pyour_jimv_db_password < ~/sites/JimV-C/misc/init.sql
# 确认是否初始化成功
mysql -u jimv -pyour_jimv_db_password -e 'show databases'
```

## 修改配置文件

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
| **`db_password`** | your_jimv_db_password   | 连接数控的密码     |
| redis_host        | localhost               | redis数据库地址   |
| redis_port        | 6379                    | redis数据库端口   |
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


## 启动服务

```bash
sudo mkdir -p /var/log/jimv
sudo chown www.www /var/log/jimv
# 进入JimV-C目录
cd ~/sites/JimV-C
# 启动JimV-C
gunicorn -c gunicorn_config.py main:app
```

## 部署 Nginx

``` bash
# 安装 Nginx
yum install nginx -y

# 配置 Nginx
sed -i 's@^user nginx;@user www;@g' /etc/nginx/nginx.conf
chown -R www.www /var/log/nginx

# 启动并使其随机启动
systemctl enable nginx.service
systemctl start nginx.service
```

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

