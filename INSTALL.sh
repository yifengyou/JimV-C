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
export JIMVC_REPOSITORY_URL='https://raw.githubusercontent.com/jamesiter/JimV-C'
export EDITION='master'
export NGINX_JIMV_URL=${JIMVC_REPOSITORY_URL}'/'${EDITION}'/misc/nginx_jimv.conf'
export GENERATE_PASSWORD_SCRIPT_TMP_PATH='/tmp/gen_pswd.sh'
export SMTP_HOST=''
export SMTP_USER=''
export SMTP_PASSWORD=''

ARGS=`getopt -o h --long rdb_root_password:,rdb_jimv_password:,redis_password:,jwt_secret:,secret_key:,help -n 'INSTALL.sh' -- "$@"`

eval set -- "${ARGS}"

while true
do
    case "$1" in
        --rdb_root_password)
            export RDB_ROOT_PSWD=$2
            shift 2
            ;;
        --rdb_jimv_password)
            export RDB_JIMV_PSWD=$2
            shift 2
            ;;
        --redis_password)
            export REDIS_PSWD=$2
            shift 2
            ;;
        --jwt_secret)
            export JWT_SECRET=$2
            shift 2
            ;;
        --secret_key)
            export SECRET_KEY=$2
            shift 2
            ;;
        -h|--help)
            echo 'INSTALL.sh [-h|--help|--rdb_root_password|--rdb_jimv_password|--redis_password|--jwt_secret|--secret_key]'
            exit 0
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Internal error!"
            exit 1
            ;;
    esac
done

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

    if [ ! -e ${GENERATE_PASSWORD_SCRIPT_TMP_PATH} ]; then
        curl ${JIMVC_REPOSITORY_URL}'/'${EDITION}'/misc/gen_pswd.sh' -o ${GENERATE_PASSWORD_SCRIPT_TMP_PATH}
        chmod +x ${GENERATE_PASSWORD_SCRIPT_TMP_PATH}
    fi

    if [ ! ${RDB_ROOT_PSWD} ] || [ ${#RDB_ROOT_PSWD} -eq 0 ]; then
        export RDB_ROOT_PSWD=`${GENERATE_PASSWORD_SCRIPT_TMP_PATH}`
    fi

    if [ ! ${RDB_JIMV_PSWD} ] || [ ${#RDB_JIMV_PSWD} -eq 0 ]; then
        export RDB_JIMV_PSWD=`${GENERATE_PASSWORD_SCRIPT_TMP_PATH}`
    fi

    if [ ! ${REDIS_PSWD} ] || [ ${#REDIS_PSWD} -eq 0 ]; then
        export REDIS_PSWD=`${GENERATE_PASSWORD_SCRIPT_TMP_PATH} 128`
    fi

    if [ ! ${JWT_SECRET} ] || [ ${#JWT_SECRET} -eq 0 ]; then
        export JWT_SECRET=`${GENERATE_PASSWORD_SCRIPT_TMP_PATH} 128`
    fi

    if [ ! ${SECRET_KEY} ] || [ ${#SECRET_KEY} -eq 0 ]; then
        export SECRET_KEY=`${GENERATE_PASSWORD_SCRIPT_TMP_PATH} 128`
    fi

    rm -f ${GENERATE_PASSWORD_SCRIPT_TMP_PATH}

    yum install epel-release -y
    yum install python2-pip git -y
    pip install --upgrade pip -i ${PYPI}
    pip install virtualenv -i ${PYPI}
}

function clear_up_environment() {
    systemctl stop firewalld
    systemctl disable firewalld
    systemctl stop NetworkManager
    systemctl disable NetworkManager

    sed -i 's@SELINUX=enforcing@SELINUX=disabled@g' /etc/sysconfig/selinux
    sed -i 's@SELINUX=enforcing@SELINUX=disabled@g' /etc/selinux/config
    setenforce 0
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
${RDB_ROOT_PSWD}
${RDB_ROOT_PSWD}
Y
Y
Y
Y
EOF

    # 测试是否部署成功
    mysql -u root -p${RDB_ROOT_PSWD} -e 'show databases'
}

function install_Redis() {
    # 安装 Redis
    yum install redis -y

    # 配置 Redis
    echo 'vm.overcommit_memory = 1' >> /etc/sysctl.conf
    sysctl -p
    sed -i 's@^daemonize no@daemonize yes@g' /etc/redis.conf
    sed -i 's@^bind 127.0.0.1@bind 0.0.0.0@g' /etc/redis.conf
    sed -i 's@^appendonly no@appendonly yes@g' /etc/redis.conf
    echo "requirepass ${REDIS_PSWD}" >> /etc/redis.conf

    # 启动并使其随机启动
    systemctl enable redis.service
    systemctl start redis.service
}

function install_Nginx() {
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
}

function create_web_user() {
    useradd -m www
}

function create_web_sites_directory() {
    su - www -c "mkdir ~/sites"
}

function clone_and_checkout_JimVC() {
    su - www -c "git clone https://github.com/jamesiter/JimV-C.git ~/sites/JimV-C"
}

function install_dependencies_library() {
    # 创建 python 虚拟环境
    su - www -c "virtualenv --system-site-packages ~/venv"

    # 导入 python 虚拟环境
    su - www -c "source ~/venv/bin/activate"

    # 使切入 www 用户时自动导入 python 虚拟环境
    su - www -c "echo '. ~/venv/bin/activate' >> .bashrc"

    # 安装 JimV-C 所需扩展库
    su - www -c "pip install -r ~/sites/JimV-C/requirements.txt -i ${PYPI}"
}

function fit_www_user_permission() {
    mkdir -p /var/log/jimv
    chown www.www /var/log/jimv

    mkdir -p /run/jimv
    chown www.www /run/jimv
}

function initialization_db() {
    # 建立 JimV 数据库专属用户
    mysql -u root -p${RDB_ROOT_PSWD} -e "grant all on jimv.* to jimv@localhost identified by \"${RDB_JIMV_PSWD}\"; flush privileges"

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

function display_summary_information() {
    echo
    echo "=== Summary information"
    echo "RDB root password: [${RDB_ROOT_PSWD}]"
    echo "RDB jimv password: [${RDB_JIMV_PSWD}]"
    echo "Redis port: [6379]"
    echo "Redis password: [${REDIS_PSWD}]"
    echo "======================="
    echo
    echo "Now, you can run JimV-C use command '/home/www/sites/JimV-C/startup.sh'."
}

function deploy() {
    check_precondition
    clear_up_environment
    prepare
    create_web_user
    create_web_sites_directory
    clone_and_checkout_JimVC
    fit_www_user_permission
    install_MariaDB
    install_Redis
    install_Nginx
    install_dependencies_library
    initialization_db
    generate_config_file
    display_summary_information
}

deploy

