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
export SMTP_HOST=''
export SMTP_USER=''
export SMTP_PASSWORD=''
export TOKEN=`echo $[$RANDOM]|md5sum|cut -c 1-32`

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
        if [[ ${VERSION_ID} -lt 7 ]]; then
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

    if [[  "x_"${answer} != "x_Y" ]] && [[ "x_"${answer} != "x_y" ]]; then
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

    if [[ ! ${JIMV_VERSION} ]] || [[ ${#JIMV_VERSION} -eq 0 ]]; then
        export JIMV_VERSION='master'
    fi

    yum install epel-release -y
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

function install_JimVC() {
    cat > /etc/yum.repos.d/JimV.repo << EOF
[JimV]
name=JimV - \$basearch
baseurl=http://repo.jimv.cn/centos/7/os/\$basearch
        http://repo.jimv.io/centos/7/os/\$basearch
        http://repo.iit.im/centos/7/os/\$basearch
failovermethod=priority
enabled=1
gpgcheck=0
gpgkey=https://repo.jimv.cn/RPM-GPG-KEY-JIMV-114EA591
EOF
    yum install jimv-controller -y
}

function generate_passwords() {
    export GENERATE_PASSWORD_SCRIPT='/usr/bin/gen_pswd.sh'

    if [[ ! ${RDB_ROOT_PSWD} ]] || [[ ${#RDB_ROOT_PSWD} -eq 0 ]]; then
        export RDB_ROOT_PSWD=`${GENERATE_PASSWORD_SCRIPT}`
    fi

    if [[ ! ${RDB_JIMV_PSWD} ]] || [[ ${#RDB_JIMV_PSWD} -eq 0 ]]; then
        export RDB_JIMV_PSWD=`${GENERATE_PASSWORD_SCRIPT}`
    fi

    if [[ ! ${REDIS_PSWD} ]] || [[ ${#REDIS_PSWD} -eq 0 ]]; then
        export REDIS_PSWD=`${GENERATE_PASSWORD_SCRIPT} 128`
    fi

    if [[ ! ${JWT_SECRET} ]] || [[ ${#JWT_SECRET} -eq 0 ]]; then
        export JWT_SECRET=`${GENERATE_PASSWORD_SCRIPT} 128`
    fi

    if [[ ! ${SECRET_KEY} ]] || [[ ${#SECRET_KEY} -eq 0 ]]; then
        export SECRET_KEY=`${GENERATE_PASSWORD_SCRIPT} 128`
    fi
}

function create_web_user() {
    useradd -M www
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
    cat /usr/share/jimv/controller/misc/nginx_jimv.conf >> /etc/nginx/nginx.conf

    # 启动并使其随机启动
    systemctl enable nginx.service
    systemctl start nginx.service
}

function initialization_db() {
    # 建立 JimV 数据库专属用户
    mysql -u root -p${RDB_ROOT_PSWD} -e "grant all on jimv.* to jimv@localhost identified by \"${RDB_JIMV_PSWD}\"; flush privileges"

    # 初始化数据库
    mysql -u jimv -p${RDB_JIMV_PSWD} < /usr/share/jimv/controller/misc/init.sql

    # 确认是否初始化成功
    mysql -u jimv -p${RDB_JIMV_PSWD} -e 'show databases'
}

function generate_token() {
    redis-cli -a ${REDIS_PSWD} --raw ZADD Z:Token $(($(date +%s) + 86400)) ${TOKEN}
}

function generate_config_file() {
    sed -i "s/\"db_password\".*$/\"db_password\": \"${RDB_JIMV_PSWD}\",/" /etc/jimvc.conf
    sed -i "s/\"redis_password\".*$/\"redis_password\": \"${REDIS_PSWD}\",/" /etc/jimvc.conf
    sed -i "s/\"jwt_secret\".*$/\"jwt_secret\": \"${JWT_SECRET}\",/" /etc/jimvc.conf
    sed -i "s/\"SECRET_KEY\".*$/\"SECRET_KEY\": \"${SECRET_KEY}\",/" /etc/jimvc.conf
    sed -i "s/\"smtp_host\".*$/\"smtp_host\": \"${SMTP_HOST}\",/" /etc/jimvc.conf
    sed -i "s/\"smtp_user\".*$/\"smtp_user\": \"${SMTP_USER}\",/" /etc/jimvc.conf
    sed -i "s/\"smtp_password\".*$/\"smtp_password\": \"${SMTP_PASSWORD}\",/" /etc/jimvc.conf
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
    echo "curl https://raw.githubusercontent.com/jamesiter/JimV-N/master/INSTALL.sh | bash -s -- --host `hostname -I` --token ${TOKEN}"
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
    create_web_user
    install_JimVC
    generate_passwords
    install_MariaDB
    install_Redis
    install_Nginx
    initialization_db
    generate_token
    generate_config_file
    start_JimVC
    display_summary_information
}

deploy

