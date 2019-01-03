#!/usr/bin/env bash

systemctl stop jimvn
systemctl stop jimvc

deactivate
mysql -u jimv -p < update.sql

DEL S:IP:Used
DEL S:IP:Available
DEL S:VNCPort:Used
DEL S:VNCPort:Available
DEL H:GlobalConfig

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

rm -f /etc/systemd/system/jimvc.service
rm -rf /usr/local/venv-jimv
rm -rf /usr/local/JimV-C

yum install jimv-controller -y
systemctl daemon-reload
systemctl restart jimvc
