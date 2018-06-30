# 手动安装

[TOC]: # "手动安装"

# 手动安装
- [声明全局变量](#声明全局变量)
- [安装必要软件](#安装必要软件)
- [开启 NTP 同步](#开启-ntp-同步)
- [配置 `/etc/hosts` 文件](#配置-etchosts-文件)
- [服务器间实现SSH-KEY互通(为热迁移做铺垫)](#服务器间实现ssh-key互通为热迁移做铺垫)
    - [生成空密码 RSA 密钥对](#生成空密码-rsa-密钥对)
    - [生成与密钥对适配的 `~/.ssh/authorized_keys` 文件](#生成与密钥对适配的-sshauthorized-keys-文件)
    - [复制 `~/.ssh` 目录到集群中的其它计算节点上](#复制-ssh-目录到集群中的其它计算节点上)
- [同步 `/etc/hosts` 文件](#同步-etchosts-文件)
- [清理环境](#清理环境)
- [部署 MariaDB](#部署-mariadb)
- [部署 Redis](#部署-redis)
- [创建 Web 用户](#创建-web-用户)
- [创建站点发布目录](#创建站点发布目录)
- [克隆 JimV-C 项目](#克隆-jimv-c-项目)
- [安装所需库](#安装所需库)
- [适配 www 用户权限](#适配-www-用户权限)
- [初始化JimV MySQL数据库](#初始化jimv-mysql数据库)
- [修改配置文件](#修改配置文件)
- [启动服务](#启动服务)
- [部署 Nginx](#部署-nginx)
- [测试 JimV-C 是否安装成功](#测试-jimv-c-是否安装成功)


## 声明全局变量

``` bash
export PYPI='https://mirrors.aliyun.com/pypi/simple/'
export JIMVC_REPOSITORY_URL='https://raw.githubusercontent.com/jamesiter/JimV-C'
export EDITION='master'
export NGINX_JIMV_URL=${JIMVC_REPOSITORY_URL}'/'${EDITION}'/misc/nginx_jimv.conf'
export GENERATE_PASSWORD_SCRIPT_TMP_PATH='/tmp/gen_pswd.sh'
export SYNC_SSH_KEY_PAIR_SCRIPT_PATH='/usr/sbin/sync_ssh_key_pair.sh'
export SYNC_HOSTS_FILE_SCRIPT_PATH='/usr/sbin/sync_hosts_file.sh'
export SMTP_HOST=''
export SMTP_USER=''
export SMTP_PASSWORD=''

curl ${JIMVC_REPOSITORY_URL}'/'${EDITION}'/misc/gen_pswd.sh' -o ${GENERATE_PASSWORD_SCRIPT_TMP_PATH}
chmod +x ${GENERATE_PASSWORD_SCRIPT_TMP_PATH}

export RDB_ROOT_PSWD=`${GENERATE_PASSWORD_SCRIPT_TMP_PATH}`
export RDB_JIMV_PSWD=`${GENERATE_PASSWORD_SCRIPT_TMP_PATH}`
export REDIS_PSWD=`${GENERATE_PASSWORD_SCRIPT_TMP_PATH} 128`
export JWT_SECRET=`${GENERATE_PASSWORD_SCRIPT_TMP_PATH} 128`
export SECRET_KEY=`${GENERATE_PASSWORD_SCRIPT_TMP_PATH} 128`

rm -f ${GENERATE_PASSWORD_SCRIPT_TMP_PATH}
```


## 安装必要软件

``` bash
yum install epel-release python2-pip git psmisc -y
pip install --upgrade pip -i ${PYPI}
pip install virtualenv -i ${PYPI}
```


## 开启 NTP 同步

``` bash
timedatectl set-timezone Asia/Shanghai
timedatectl set-ntp true
timedatectl status
```


## 配置 `/etc/hosts` 文件

``` text
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
192.168.2.253    jimvc.jimv.io
192.168.2.221    jimvn01.jimv.io
192.168.2.222    jimvn02.jimv.io
192.168.2.223    jimvn03.jimv.io
192.168.2.224    jimvn04.jimv.io
```


## 服务器间实现SSH-KEY互通(为热迁移做铺垫)

### 生成空密码 RSA 密钥对

``` bash
# 生成空密码的SSH使用的密钥对
# 一路回车
ssh-keygen
```

### 生成与密钥对适配的 `~/.ssh/authorized_keys` 文件

``` bash
# 接下来将会把包含 authorized_keys 文件的 ~/.ssh 目录复制到其它计算节点上
ssh-copy-id localhost
```

### 复制 `~/.ssh` 目录到集群中的其它计算节点上

``` bash
curl ${JIMVC_REPOSITORY_URL}'/'${EDITION}'/misc/sync_ssh_key_pair.sh' -o ${SYNC_SSH_KEY_PAIR_SCRIPT_PATH}
chmod +x ${SYNC_SSH_KEY_PAIR_SCRIPT_PATH}
${SYNC_SSH_KEY_PAIR_SCRIPT_PATH}
```


## 同步 `/etc/hosts` 文件

> `注意：` 每次有新的节点加入进来，都需要同步一次该文件

``` bash
curl ${JIMVC_REPOSITORY_URL}'/'${EDITION}'/misc/sync_hosts_file.sh' -o ${SYNC_HOSTS_FILE_SCRIPT_PATH}
chmod +x ${SYNC_HOSTS_FILE_SCRIPT_PATH}
${SYNC_HOSTS_FILE_SCRIPT_PATH}
```


## 清理环境

``` bash
systemctl stop firewalld
systemctl disable firewalld
systemctl stop NetworkManager
systemctl disable NetworkManager

sed -i 's@SELINUX=enforcing@SELINUX=disabled@g' /etc/sysconfig/selinux
sed -i 's@SELINUX=enforcing@SELINUX=disabled@g' /etc/selinux/config
setenforce 0
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
${RDB_ROOT_PSWD}
${RDB_ROOT_PSWD}
Y
Y
Y
Y
EOF

# 测试是否部署成功
mysql -u root -p${RDB_ROOT_PSWD} -e 'show databases'
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
echo "requirepass ${REDIS_PSWD}" >> /etc/redis.conf

# 启动并使其随机启动
systemctl enable redis.service
systemctl start redis.service
```


## 创建 Web 用户

```bash
useradd -m www
```


## 创建站点发布目录

```bash
su - www -c "mkdir ~/sites"
```


## 克隆 JimV-C 项目

```bash
su - www -c "git clone https://github.com/jamesiter/JimV-C.git ~/sites/JimV-C"
```


## 安装所需库

```bash
# 创建 python 虚拟环境
su - www -c "virtualenv --system-site-packages ~/venv"

# 导入 python 虚拟环境
su - www -c "source ~/venv/bin/activate"

# 使切入 www 用户时自动导入 python 虚拟环境
su - www -c "echo '. ~/venv/bin/activate' >> .bashrc"

# 安装JimV-C所需扩展库
su - www -c "pip install -r ~/sites/JimV-C/requirements.txt -i ${PYPI}"
```


## 适配 www 用户权限

``` bash
mkdir -p /var/log/jimv
chown www.www /var/log/jimv

mkdir -p /run/jimv
chown www.www /run/jimv
```


## 初始化JimV MySQL数据库

```bash
# 建立 JimV 数据库专属用户
mysql -u root -p${RDB_ROOT_PSWD} -e "grant all on jimv.* to jimv@localhost identified by \"${RDB_JIMV_PSWD}\"; flush privileges"
# 初始化数据库
su - www -c "mysql -u jimv -p${RDB_JIMV_PSWD} < ~/sites/JimV-C/misc/init.sql"
# 确认是否初始化成功
mysql -u jimv -p${RDB_JIMV_PSWD} -e 'show databases'
```


## 修改配置文件

配置文件的默认读取路径：`/etc/jimvc.conf`
``` bash
cp -v /home/www/sites/JimV-C/jimvc.conf /etc/jimvc.conf
sed -i "s/\"db_password\".*$/\"db_password\": \"${RDB_JIMV_PSWD}\",/" /etc/jimvc.conf
sed -i "s/\"redis_password\".*$/\"redis_password\": \"${REDIS_PSWD}\",/" /etc/jimvc.conf
sed -i "s/\"jwt_secret\".*$/\"jwt_secret\": \"${JWT_SECRET}\",/" /etc/jimvc.conf
sed -i "s/\"SECRET_KEY\".*$/\"SECRET_KEY\": \"${SECRET_KEY}\",/" /etc/jimvc.conf
sed -i "s/\"smtp_host\".*$/\"smtp_host\": \"${SMTP_HOST}\",/" /etc/jimvc.conf
sed -i "s/\"smtp_user\".*$/\"smtp_user\": \"${SMTP_USER}\",/" /etc/jimvc.conf
sed -i "s/\"smtp_password\".*$/\"smtp_password\": \"${SMTP_PASSWORD}\",/" /etc/jimvc.conf
```
**提示：**
> 下表中凸显的配置项，需要用户根据自己的环境手动修改。

| 配置项            | 默认值                   | 说明              |
|:-----------------|:------------------------|:-----------------|
| listen           | 127.0.0.1               | JimV-C 侦听的地址 |
| port             | 8008                    | JimV-C 侦听的端口 |
| db_name          | jimv                    | 数据库名称        |
| db_host          | localhost               | 数据库地址        |
| db_port          | 3306                    | 数据库端口        |
| db_user          | jimv                    | 连接数控的用户名   |
| **`db_password`**                         || 连接数控的密码     |
| redis_host       | localhost               | redis数据库地址   |
| redis_port       | 6379                    | redis数据库端口   |
| **`redis_password`**                      || redis数据库密码   |
| redis_dbid       | 0                       | 连接的redis数据库  |
| log_file_path    | /var/log/jimv/jimvc.log | 日志存储路径       |
| **`jwt_secret`**                          || token安全码       |
| **`SECRET_KEY`** |                         | session安全码     |
| **`smtp_host`**                           || SMTP 服务器地址   |
| smtp_port        | 25                      | SMTP 服务器端口   |
| **`smtp_user`**                           || SMTP 用户         |
| **`smtp_password`**                       || SMTP 密码         |
| smtp_starttls    | true                    | SMTP 是否开启 TLS |


## 启动服务

```bash
# 启动JimV-C
/home/www/sites/JimV-C/startup.sh
```


## 部署 Nginx

``` bash
# 安装 Nginx
yum install nginx -y

# 配置 Nginx
mkdir -p /etc/jimv/keys
chown -R www.www /var/lib/nginx
sed -i 's@user nginx.*$@user www;@' /etc/nginx/nginx.conf
sed -i '/^.*server {/,$d' /etc/nginx/nginx.conf
curl ${NGINX_JIMV_URL} >> /etc/nginx/nginx.conf

# 启动并使其随机启动
systemctl enable nginx.service
systemctl start nginx.service
```


## 测试 JimV-C 是否安装成功

> 通过浏览器打开 JimV-C 地址。如果展现出初始化页面，则表示安装成功。
