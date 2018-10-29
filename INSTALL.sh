#!/usr/bin/env bash
#
# JimV-C
#
# Copyright (C) 2017 JimV <james.iter.cn@gmail.com>
#
# Author: James Iter <james.iter.cn@gmail.com>
#
#   This script will help you to automation install JimV-C.
#
# Example:
#   Pass arguments to the installer.
#   curl https://raw.githubusercontent.com/jamesiter/JimV-C/dev/INSTALL.sh | bash -s -- --version dev
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/jamesiter/JimV-C/dev/INSTALL.sh)" -- --version dev

export PYPI='https://mirrors.aliyun.com/pypi/simple/'
export JIMVC_REPOSITORY_RAW_URL='https://raw.githubusercontent.com/jamesiter/JimV-C'
export JIMVC_DOWNLOAD_URL='https://github.com/jamesiter/JimV-C/archive/master.tar.gz'
export JIMVC_PATH='/usr/local/JimV-C'
export GENERATE_PASSWORD_SCRIPT_TMP_PATH='/tmp/gen_pswd.sh'
export SMTP_HOST=''
export SMTP_USER=''
export SMTP_PASSWORD=''

ARGS=`getopt -o h --long rdb_root_password:,rdb_jimv_password:,redis_password:,jwt_secret:,secret_key:,version:,help -n 'INSTALL.sh' -- "$@"`

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
        --version)
            export JIMV_VERSION=$2
            export JIMVC_DOWNLOAD_URL=$(sed s@master@${JIMV_VERSION}@ <<< ${JIMVC_DOWNLOAD_URL})
            shift 2
            ;;
        -h|--help)
            echo 'INSTALL.sh [-h|--help|--rdb_root_password|--rdb_jimv_password|--redis_password|--jwt_secret|--secret_key|--version]'
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

function ensure_hosts_layout() {
    echo "______________________________________________________________________________"
    /bin/cat /etc/hosts
    echo
    read -p "您已经布局好 /etc/hosts 了吗 [Y/N]? " answer

    if [  "x_"${answer} != "x_Y" ] && [ "x_"${answer} != "x_y" ]; then
        echo "OK, good bye!";
        exit 0
    fi
}

function sync_ssh_key_pair() {
    sed -i 's@.*StrictHostKeyChecking.*@StrictHostKeyChecking no@' /etc/ssh/ssh_config

    rm -f ~/.ssh/id_rsa ~/.ssh/id_rsa.pub; echo -e "\n\n\n" | ssh-keygen -N ""
    echo >> ~/.ssh/authorized_keys
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
    chmod 0600 ~/.ssh/authorized_keys

    DHOSTS=`egrep -v '^$|localhost|jimvc' /etc/hosts | awk '{ print $1; }'`

    for dhost in ${DHOSTS}
    do
        scp -r ~/.ssh ${dhost}:~/
        # 关闭 SSH 服务器端 Key 校验
        ssh ${dhost} "sed -i 's@.*StrictHostKeyChecking.*@StrictHostKeyChecking no@' /etc/ssh/ssh_config"
    done
}

function sync_hosts_file() {
    DHOSTS=`egrep -v '^$|localhost|jimvc' /etc/hosts | awk '{ print $1; }'`

    for dhost in ${DHOSTS}
    do
        scp /etc/hosts ${dhost}:/etc/hosts
    done
}

function prepare() {

    if [ ! ${JIMV_VERSION} ] || [ ${#JIMV_VERSION} -eq 0 ]; then
        export JIMV_VERSION='master'
    fi

    if [ ! -e ${GENERATE_PASSWORD_SCRIPT_TMP_PATH} ]; then
        curl ${JIMVC_REPOSITORY_RAW_URL}'/'${JIMV_VERSION}'/misc/gen_pswd.sh' -o ${GENERATE_PASSWORD_SCRIPT_TMP_PATH}
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
    yum install python2-pip git psmisc -y
    pip install --upgrade pip -i ${PYPI}
    pip install virtualenv -i ${PYPI}
}

function set_ntp() {
    yum install ntp -y
    systemctl start ntpd
    systemctl enable ntpd
    timedatectl set-timezone Asia/Shanghai
    timedatectl set-ntp true
    timedatectl status
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
    sed -i '/\[mysqld\]/a\max_connections = 10000' /etc/my.cnf

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
    export NGINX_JIMV_URL=${JIMVC_REPOSITORY_RAW_URL}'/'${JIMV_VERSION}'/misc/nginx_jimv.conf'

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
    useradd -M www
}

function get_JimVC() {
    mkdir -p ${JIMVC_PATH}
    curl -sL ${JIMVC_DOWNLOAD_URL} | tar -zxf - --strip-components 1 -C ${JIMVC_PATH}
}

function install_dependencies_library() {
    mkdir -p ~/.pip
    cat > ~/.pip/pip.conf << EOF
[global]
index-url = ${PYPI}
EOF

    # 创建 python 虚拟环境
    virtualenv --system-site-packages /usr/local/venv-jimv

    # 导入 python 虚拟环境
    source /usr/local/venv-jimv/bin/activate

    # 自动导入 python 虚拟环境
    echo '. /usr/local/venv-jimv/bin/activate' >> ~/.bashrc

    # 安装 JimV-C 所需扩展库
    grep -v "^#" ${JIMVC_PATH}/requirements.txt | xargs -n 1 pip install -i ${PYPI}
}

function initialization_db() {
    # 建立 JimV 数据库专属用户
    mysql -u root -p${RDB_ROOT_PSWD} -e "grant all on jimv.* to jimv@localhost identified by \"${RDB_JIMV_PSWD}\"; flush privileges"

    # 初始化数据库
    mysql -u jimv -p${RDB_JIMV_PSWD} < ${JIMVC_PATH}/misc/init.sql

    # 确认是否初始化成功
    mysql -u jimv -p${RDB_JIMV_PSWD} -e 'show databases'
}

function generate_config_file() {
    cp -v ${JIMVC_PATH}/jimvc.conf /etc/jimvc.conf
    sed -i "s/\"db_password\".*$/\"db_password\": \"${RDB_JIMV_PSWD}\",/" /etc/jimvc.conf
    sed -i "s/\"redis_password\".*$/\"redis_password\": \"${REDIS_PSWD}\",/" /etc/jimvc.conf
    sed -i "s/\"jwt_secret\".*$/\"jwt_secret\": \"${JWT_SECRET}\",/" /etc/jimvc.conf
    sed -i "s/\"SECRET_KEY\".*$/\"SECRET_KEY\": \"${SECRET_KEY}\",/" /etc/jimvc.conf
    sed -i "s/\"smtp_host\".*$/\"smtp_host\": \"${SMTP_HOST}\",/" /etc/jimvc.conf
    sed -i "s/\"smtp_user\".*$/\"smtp_user\": \"${SMTP_USER}\",/" /etc/jimvc.conf
    sed -i "s/\"smtp_password\".*$/\"smtp_password\": \"${SMTP_PASSWORD}\",/" /etc/jimvc.conf

    cp -v /usr/local/JimV-C/misc/jimvc.service /etc/systemd/system/jimvc.service
    systemctl daemon-reload
}

function start_JimVC() {
    systemctl start jimvc.service
    systemctl enable jimvc.service
}

function display_summary_information() {
    echo
    echo "=== 信息汇总"
    echo "MariaDB root 密码: [${RDB_ROOT_PSWD}]"
    echo "MariaDB jimv 密码: [${RDB_JIMV_PSWD}]"
    echo "Redis 端口: [6379]"
    echo "Redis 密码: [${REDIS_PSWD}]"
    echo "======================="
    echo
    echo "JimV-C 已经安装完成，您再需如下几步就能完成整个 JimV 的部署: "
    echo
    echo "--->"
    echo "1: 通过 Web 页面 http://`hostname -I` 初始化 JimV-C。"
    echo
    echo "--->"
    echo "2: 到 [计算节点] 执行如下命令，进行 JimV-N 的部署。"
    echo "curl https://raw.githubusercontent.com/jamesiter/JimV-N/master/INSTALL.sh | bash -s -- --redis_host `hostname -I` --redis_password ${REDIS_PSWD} --redis_port 6379"
    echo
    echo "--->"
    echo "3: 享受 JimV 给您带来的 '简单、快速、灵活' 开创虚拟机实例的快乐。。。。。"
    echo
}

function deploy() {
    check_precondition
    clear_up_environment
    ensure_hosts_layout
    sync_ssh_key_pair
    sync_hosts_file
    prepare
    set_ntp
    create_web_user
    get_JimVC
    install_MariaDB
    install_Redis
    install_Nginx
    install_dependencies_library
    initialization_db
    generate_config_file
    start_JimVC
    display_summary_information
}

deploy

