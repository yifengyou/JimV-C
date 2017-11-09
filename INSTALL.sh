#!/usr/bin/env bash
#
# JimV-C
#
# Copyright (C) 2017 JimV <james.iter.cn@gmail.com>
#
# Author: James Iter <james.iter.cn@gmail.com>
#
#  This script will help you to automation install JimV-C.
#

export PYPI='https://mirrors.aliyun.com/pypi/simple/'
export RDB_PSWD='your_rdb_root_password'
export RDB_JIMV_PSWD='your_rdb_jimv_password'
export REDIS_PSWD='your_jimv_redis_passwordddddddddddddddddddddddddddddddddddddddddddddddddddddddd'
export JWT_SECRET='kcMsj4qj0EAvAvj3nlFlPZd2x7P9kBBQ$deae64883a03982913e6c5f0ba265c2c5dfd0cfx'
export SECRET_KEY='QSYI73re6x553wmcNwT9tk4OCNK9OUS9xNUulDShEcvRw00YhCKaqHhEGYOGKOSB'
export SMTP_HOST=''
export SMTP_USER=''
export SMTP_PASSWORD=''

function check_precondition() {
    source /etc/os-release
    case ${ID} in
    centos|fedora|rhel)
        if [ ${VERSION_ID} -lt 7 ]; then
            echo "System version must greater than or equal to 7, We found ${VERSION_ID}."
	        exit 1
        fi
        ;;
    *)
        echo "${ID} is unknown, Please to be installed manually."
	    exit 1
        ;;
    esac
}

function prepare() {
    yum install python2-pip git -y
    pip install --upgrade pip -i ${PYPI}
    pip install virtualenv -i ${PYPI}
}

function install_MariaDB() {
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
${RDB_PSWD}
${RDB_PSWD}
Y
Y
Y
Y
EOF

    # 测试是否部署成功
    mysql -u root -p${RDB_PSWD} -e 'show databases'
}

function install_Redis() {
    # 安装 Redis
    yum install redis -y

    # 配置 Redis
    echo 'vm.overcommit_memory = 1' >> /etc/sysctl.conf
    sysctl -p
    sed -i '@^daemonize no@daemonize yes@g' /etc/redis.conf
    sed -i 's@^bind 127.0.0.1@bind 0.0.0.0@g' /etc/redis.conf
    sed -i 's@^appendonly no@appendonly yes@g' /etc/redis.conf
    echo 'requirepass ${REDIS_PSWD}' >> /etc/redis.conf

    # 启动并使其随机启动
    systemctl enable redis.service
    systemctl start redis.service
}

function create_web_user() {
    useradd -m www
}

function create_web_sites_directory() {
    su - www -c "mkdir ~/sites"
}

function clone_and_checkout_JimV-C() {
    su - www -c "git clone https://github.com/jamesiter/JimV-C.git ~/sites/JimV-C"
}

function install_dependencies_library() {
    # 创建 python 虚拟环境
    su - www -c "virtualenv --system-site-packages ~/venv"

    # 导入 python 虚拟环境
    su - www -c "source ~/venv/bin/activate"

    # 使切入 www 用户时自动导入 python 虚拟环境
    su - www -c "echo '. ~/venv/bin/activate' >> .bashrc"

    # 安装JimV-C所需扩展库
    su - www -c "pip install -r ~/sites/JimV-C/requirements.txt -i ${PYPI}"
}

function initialization_db() {
    # 建立 JimV 数据库专属用户
    mysql -u root -p${RDB_PSWD} -e "grant all on jimv.* to jimv@localhost identified by \"${RDB_JIMV_PSWD}\"; flush privileges"

    # 初始化数据库
    su - www -c "mysql -u jimv -p${RDB_JIMV_PSWD} < ~/sites/JimV-C/misc/init.sql"

    # 确认是否初始化成功
    mysql -u jimv -p${RDB_JIMV_PSWD} -e 'show databases'
}

function generate_config_file() {
    cp -v /home/www/sites/JimV-C/jimvc.conf /etc/jimvc.conf
    sed -i "s/\"db_password\".*$/\"db_password\": \"${RDB_JIMV_PSWD}\",/" /etc/jimvc.conf
    sed -i "s/\"redis_password\".*$/\"redis_password\": \"${REDIS_PSWD}\",/" /etc/jimvc.conf
    sed -i "s/\"jwt_secret\".*$/\"jwt_secret\": \"${JWT_SECRET}\",/" /etc/jimvc.conf
    sed -i "s/\"SECRET_KEY\".*$/\"SECRET_KEY\": \"${SECRET_KEY}\",/" /etc/jimvc.conf
    sed -i "s/\"smtp_host\".*$/\"smtp_host\": \"${SMTP_HOST}\",/" /etc/jimvc.conf
    sed -i "s/\"smtp_user\".*$/\"smtp_user\": \"${SMTP_USER}\",/" /etc/jimvc.conf
    sed -i "s/\"smtp_password\".*$/\"smtp_password\": \"${SMTP_PASSWORD}\",/" /etc/jimvc.conf
}

function start() {
    mkdir -p /var/log/jimv
    chown www.www /var/log/jimv

    mkdir -p /run/jimv
    chown www.www /run/jimv
}

