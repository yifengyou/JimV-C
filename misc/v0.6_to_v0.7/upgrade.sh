#!/usr/bin/env bash

export PYPI='https://mirrors.aliyun.com/pypi/simple/'
export JIMVC_PATH='/usr/local/JimV-C'
export JIMVC_DOWNLOAD_URL='https://github.com/jamesiter/JimV-C/archive/master.tar.gz'

mkdir -p ${JIMVC_PATH}
curl -sL ${JIMVC_DOWNLOAD_URL} | tar -zxf - --strip-components 1 -C ${JIMVC_PATH}

mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = ${PYPI}
EOF

# 创建 python 虚拟环境
pip install virtualenv
virtualenv --system-site-packages /usr/local/venv-jimv

# 导入 python 虚拟环境
source /usr/local/venv-jimv/bin/activate

# 自动导入 python 虚拟环境
echo '. /usr/local/venv-jimv/bin/activate' >> ~/.bashrc

# 安装 JimV-C 所需扩展库
grep -v "^#" ${JIMVC_PATH}/requirements.txt | xargs -n 1 pip install -i ${PYPI}

cp -v /usr/local/JimV-C/misc/jimvc.service /etc/systemd/system/jimvc.service
systemctl daemon-reload

systemctl start jimvc.service
systemctl enable jimvc.service

systemctl status jimvc.service -l


