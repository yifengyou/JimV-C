#!/usr/bin/env bash
#
# JimV-StandAlone
#
# Copyright (C) 2017 JimV <james.iter.cn@gmail.com>
#
# Author: James Iter <james.iter.cn@gmail.com>
#
#   This script will help you to automation install JimV.
#

export PYPI='https://mirrors.aliyun.com/pypi/simple/'
export SMTP_HOST=''
export SMTP_USER=''
export SMTP_PASSWORD=''
export TOKEN=`echo $[$RANDOM]|md5sum|cut -c 1-32`
export SHOW_WARNING_VTX=false

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

    if [[ `egrep -c '(vmx|svm)' /proc/cpuinfo` -eq 0 ]]; then
        export SHOW_WARNING_VTX=true
    fi
}

function custom_repository_origin() {
    cat > /etc/yum.repos.d/JimV.repo << EOF
[JimV]
name=JimV - \$basearch
baseurl=http://repo.cdn.jimv.cn/centos/7/os/\$basearch
        http://repo.jimv.cn/centos/7/os/\$basearch
        http://repo.jimv.io/centos/7/os/\$basearch
failovermethod=priority
enabled=1
gpgcheck=0
gpgkey=https://repo.jimv.cn/RPM-GPG-KEY-JIMV-114EA591
EOF

    yum install epel-release -y
    yum install dstat htop iotop net-tools lsof nmap-ncat jq bind-utils bridge-utils psutils -y
    yum clean all
    yum makecache
}

function clear_up_environment() {
    systemctl stop firewalld
    systemctl disable firewalld
    systemctl stop NetworkManager
    systemctl disable NetworkManager

    sed -i 's@SELINUX=enforcing@SELINUX=disabled@g' /etc/sysconfig/selinux
    sed -i 's@SELINUX=enforcing@SELINUX=disabled@g' /etc/selinux/config
    setenforce 0

    sed -i '/\/tmp\/jimv.*/d' /usr/lib/tmpfiles.d/tmp.conf
    echo 'x /tmp/jimv*' >> /usr/lib/tmpfiles.d/tmp.conf
}

function create_web_user() {
    useradd -M www
}

function generate_ssh_key_pair() {
    sed -i 's@.*StrictHostKeyChecking.*@StrictHostKeyChecking no@' /etc/ssh/ssh_config

    rm -f ~/.ssh/id_rsa ~/.ssh/id_rsa.pub; echo -e "\n\n\n" | ssh-keygen -N ""
    echo >> ~/.ssh/authorized_keys
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
    chmod 0600 ~/.ssh/authorized_keys
}

function install_JimVC() {
    yum install jimv-controller -y
}

function install_JimVConsole() {
    yum install jimv-console -y
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
    echo 'root:'${RDB_ROOT_PSWD} > /var/log/mariadb/mariadb.secret
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
    cp -vf /usr/share/jimv/controller/misc/jimv.nginx /etc/nginx/nginx.conf
    sed -i 's@user .*nginx.*$@user www;@' /etc/nginx/nginx.conf

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

function generate_JimVC_config_file() {
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
    sleep 5
}

function Init_JimVC() {
    curl -XPOST -H "Content-Type: application/json" -d '{"storage_mode": 0, "vm_network": "net-br0", "vm_manage_network": "net-br0", "storage_path": "/opt/Images"}' http://127.0.0.1/api/config
}

function JimVN_pretreatment() {
    yum install epel-release -y
    yum install jq net-tools bind-utils -y
    yum install redis -y

    # 代替语句 ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'
    SERVER_IP=`hostname -I`; export SERVER_IP=${SERVER_IP%% *}
    export SERVER_NETMASK=`ifconfig | grep ${SERVER_IP} | grep -Eo 'netmask ?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*'`
    export GATEWAY=`route -n | grep '^0.0.0.0' | awk '{ print $2; }'`
    export DNS1=`nslookup 127.0.0.1 | grep Server | grep -Eo '([0-9]*\.){3}[0-9]*'`
    export NIC=`ifconfig | grep ${SERVER_IP} -B 1 | head -1 | cut -d ':' -f 1`
    export NODE_ID=`python -c "with open('/etc/machine-id', 'r') as f: _str = f.read().strip(); import string; import hashlib; m = hashlib.md5(); m.update(_str); print int(string.atoi(m.hexdigest(), 16).__str__()[:16])"`

    JOIN_RESPONSE=`curl http://127.0.0.1/api/misc/_join/${NODE_ID}/${TOKEN}`

    export REDIS_HOST=`echo ${JOIN_RESPONSE} | jq -r '.data.redis_host'`
    export REDIS_PORT=`echo ${JOIN_RESPONSE} | jq -r '.data.redis_port'`
    export REDIS_PSWD=`echo ${JOIN_RESPONSE} | jq -r '.data.redis_password'`
    export VM_NETWORK=`echo ${JOIN_RESPONSE} | jq -r '.data.vm_network'`
    export VM_NETWORK_MANAGE=`echo ${JOIN_RESPONSE} | jq -r '.data.vm_manage_network'`
}

function install_libvirt_and_libguestfish() {
    # 安装 libvirt
    uname -m | grep -q 'x86_64'  && echo 'centos' >/etc/yum/vars/contentdir || echo 'altarch' >/etc/yum/vars/contentdir
    yum install centos-release-qemu-ev -y
    yum install jimv-node -y
    yum install librbd1-10.2.5 -y
    chmod 666 /dev/kvm
    chown root.kvm /dev/kvm
}

function tune_linux_kernel_parameters() {
    sed -i '/^net.ipv4.ip_local_port_range/d' /etc/sysctl.conf
    echo 'net.ipv4.ip_local_port_range = 15800 20000' >> /etc/sysctl.conf
    sysctl -p
}

function handle_ssh_client_config() {
    # 关闭 SSH 服务器端 Key 校验
    sed -i 's@.*StrictHostKeyChecking.*@StrictHostKeyChecking no@' /etc/ssh/ssh_config
}

function handle_net_bonding_bridge() {
    # 参考地址: https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/7/html/networking_guide/
cat > /etc/sysconfig/network-scripts/ifcfg-${VM_NETWORK} << EOF
DEVICE=${VM_NETWORK}
NAME=${VM_NETWORK}
TYPE=Bridge
BOOTPROTO=static
ONBOOT=yes
DELAY=0
IPADDR=${SERVER_IP}
NETMASK=${SERVER_NETMASK}
GATEWAY=${GATEWAY}
DNS1=${DNS1}
DNS2=8.8.8.8
IPV6INIT=no
EOF

cat > /etc/sysconfig/network-scripts/ifcfg-bond0 << EOF
DEVICE=bond0
NAME=bond0
TYPE=Bond
BRIDGE=${VM_NETWORK}
BONDING_MASTER=yes
ONBOOT=yes
BOOTPROTO=none
BONDING_OPTS="mode=balance-alb xmit_hash_policy=layer3+4"
EOF

cat > /etc/sysconfig/network-scripts/ifcfg-${NIC} << EOF
DEVICE=${NIC}
NAME=${NIC}
TYPE=Ethernet
BOOTPROTO=none
ONBOOT=yes
MASTER=bond0
SLAVE=yes
EOF

    /etc/init.d/network restart
}

function create_network_bridge_in_libvirt() {

cat > /etc/libvirt/qemu/networks/${VM_NETWORK}.xml << EOF
<network>
    <uuid>the_uuid</uuid>
    <name>${VM_NETWORK}</name>
    <forward mode="bridge"/>
    <bridge name="${VM_NETWORK}"/>
</network>
EOF

    sed -i "s@the_uuid@`uuidgen`@" /etc/libvirt/qemu/networks/${VM_NETWORK}.xml

    # 去除默认的 default 网络定义
    rm -f /etc/libvirt/qemu/networks/default.xml /etc/libvirt/qemu/networks/autostart/default.xml

    # 使其随服务自动创建
    cd /etc/libvirt/qemu/networks/autostart/
    ln -s ../${VM_NETWORK}.xml ${VM_NETWORK}.xml
}

function start_libvirtd() {
    systemctl stop dnsmasq
    systemctl disable dnsmasq
    systemctl enable libvirtd
    systemctl start libvirtd
}

function install_NFS() {
    yum install nfs-utils -y
    mkdir -p /srv/nfs_template_images
    chown -R www.www /srv/nfs_template_images
    WWW_UID=$(id -u www)
    WWW_GID=$(id -g www)
    cat > /etc/exports << EOF
/srv/nfs_template_images    *(rw,insecure,all_squash,anonuid=${WWW_UID},anongid=${WWW_GID},sync,no_wdelay)
EOF
    systemctl start nfs
    systemctl enable nfs
}

function install_and_set_NFS_client() {
    yum install nfs-utils -y
    mkdir /opt/template_images
    sed -i "/${SERVER_IP}:\/srv\/nfs_template_images/d" /etc/fstab
    echo "${SERVER_IP}:/srv/nfs_template_images       /opt/template_images      nfs4    soft  0 0" >> /etc/fstab
    mount -a
}

function generate_JimVN_config_file() {
    sed -i "s/\"redis_host\".*$/\"redis_host\": \"${REDIS_HOST}\",/" /etc/jimvn.conf
    sed -i "s/\"redis_password\".*$/\"redis_password\": \"${REDIS_PSWD}\",/" /etc/jimvn.conf
    sed -i "s/\"redis_port\".*$/\"redis_port\": \"${REDIS_PORT}\",/" /etc/jimvn.conf
}

function start_JimVN() {
    systemctl start jimvn.service
    systemctl enable jimvn.service
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
    echo "JimV 已经安装完成，您再需如下几步就能完成整个 JimV 的部署: "
    echo
    echo "--->"
    echo "1: 登入 Web 页面 http://`hostname -I`"
    echo "   进入【系统配置】 --> 【IP 池】，配置您的 IP 池。"
    echo
    echo "--->"
    echo "2: 进入【模板镜像】 --> 【公共镜像】，添加模板。"
    echo
    echo "--->"
    echo "3: 享受 JimV 给您带来的 '简单、快速、灵活' 开创虚拟机实例的快乐。。。。。"
    echo
    if [[ ${SHOW_WARNING_VTX} = true ]]; then
        echo "警告：请检查 CPU 是否开启 VT 技术。未开启 VT 技术的计算节点，将以 QEMU 模式运行虚拟机。"
        echo
    fi
    echo "已经通过 'systemctl enable jimvc.service' 把 JimV-C 注册为随系统启动的服务。"
    echo "您还可以通过命令 'systemctl [start|stop|status] jimvc.service' 来管理本机的 JimV-C。"
    echo
    echo "已经通过 'systemctl enable jimvn.service' 把 JimV-N 注册为随系统启动的服务。"
    echo "您还可以通过命令 'systemctl [start|stop|status] jimvn.service' 来管理本机的 JimV-N。"
    echo
}

function deploy() {
    check_precondition
    custom_repository_origin
    clear_up_environment
    generate_ssh_key_pair
    create_web_user
    install_JimVC
    install_JimVConsole
    generate_passwords
    install_MariaDB
    install_Redis
    install_Nginx
    initialization_db
    generate_token
    generate_JimVC_config_file
    start_JimVC

    Init_JimVC
    JimVN_pretreatment
    install_libvirt_and_libguestfish
    tune_linux_kernel_parameters
    handle_ssh_client_config
    handle_net_bonding_bridge
    create_network_bridge_in_libvirt
    start_libvirtd
    install_NFS
    install_and_set_NFS_client
    generate_JimVN_config_file
    start_JimVN

    display_summary_information
}

deploy

