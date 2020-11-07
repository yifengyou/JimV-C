<!-- MDTOC maxdepth:6 firsth1:1 numbering:0 flatten:0 bullets:1 updateOnSave:1 -->

   - [测试时间](#测试时间)   
   - [测试环境](#测试环境)   
   - [参考文档](#参考文档)   
   - [裸机安装-完整步骤](#裸机安装-完整步骤)   
      - [ssh登陆](#ssh登陆)   
      - [Web登陆](#web登陆)   
   - [使用从git拉取源码运行](#使用从git拉取源码运行)   
      - [修改配置](#修改配置)   
      - [数据库配置](#数据库配置)   
      - [安装一些CentOS常用软件](#安装一些centos常用软件)   
   - [为什么不直接提供源码？而是pyc？？](#为什么不直接提供源码？而是pyc？？)   
   - [在已有CentOS中安装](#在已有centos中安装)   
   - [集群部署方案](#集群部署方案)   

<!-- /MDTOC -->
## 测试时间

![20201107_155119_16](image/20201107_155119_16.png)


## 测试环境

![20201107_155140_56](image/20201107_155140_56.png)

## 参考文档

* <https://jimv.cn/docs.html#>






## 裸机安装-完整步骤

* 通过 iPXE 在线自动安装 JimV。系统默认密码 ```pswd.jimv.cn```。
* 分两种情况，物理机/VMware 和 KVM 虚拟机

【物理机】或【VMWare 虚拟机】安装使用如下地址。
```
boot http://repo.jimv.cn/install.ipxe
```

【KVM】虚拟机安装使用如下地址。

```
boot http://repo.jimv.cn/install-by-kvm.ipxe
```

 * VMWare 默认不支持 iPXE，需要ipxe.iso启动引导。
* ipxe.iso下载地址:<https://jimv.cn/assets/ipxe.iso>

![20201107_155232_44](image/20201107_155232_44.png)

![20201107_155252_41](image/20201107_155252_41.png)

* ipxe网络启动
* 加载内核

![20201107_155257_66](image/20201107_155257_66.png)

![20201107_155305_26](image/20201107_155305_26.png)

* 启动anaconda安装流程。安装各个包

![20201107_155549_95](image/20201107_155549_95.png)

![20201107_160132_14](image/20201107_160132_14.png)

* 安装完成后会自动重启

![20201107_160553_44](image/20201107_160553_44.png)

* 内核还是3.10，有点老了呢

![20201107_160559_36](image/20201107_160559_36.png)

![20201107_160630_79](image/20201107_160630_79.png)

* 整个安装过程大约半小时，视机器性能以及网络带宽会有所不同
* 启动完成后显示该界面。默认ip是VMware NAT分配的地址，不同VMware配置不同

### ssh登陆

![20201107_160912_68](image/20201107_160912_68.png)

![20201107_161019_34](image/20201107_161019_34.png)

* 登陆用户名：```root```
* 登陆密码：```pswd.jimv.cn```

### Web登陆

![20201107_161341_51](image/20201107_161341_51.png)

* 打开浏览器，输入地址，翻车了。。尴尬。为什么嘞？
* 关机，配置VMware还原点，重启试试

![20201107_161631_34](image/20201107_161631_34.png)

* 查看nginx日志

![20201107_163347_59](image/20201107_163347_59.png)

* 检查8008端口是否有服务，发现服务挂掉了，用```journalctl -xe -u jimvc```查看一下日志

![20201107_163447_83](image/20201107_163447_83.png)

![20201107_163553_88](image/20201107_163553_88.png)

![20201107_163613_30](image/20201107_163613_30.png)

![20201107_170231_30](image/20201107_170231_30.png)

* 满屏报错。python 2退休了，还没换到python 3，看来这项目还要不少可以做的工作
* 日志定位在```/var/log/jimv```目录下，发现默认无法运行，看来测试不充分呐
* 一方面python包依赖问题没有处理妥当，另外数据库也没有初始化..

![20201107_201228_54](image/20201107_201228_54.png)

![20201107_201248_28](image/20201107_201248_28.png)

* 当我看到错误中提示缺少license字段...我选择放弃，尝试旧版本

![20201107_201638_50](image/20201107_201638_50.png)

* 草率了，重头来过，发现mariadb配置更新了，默认不给登陆。这么搞

![20201107_204413_99](image/20201107_204413_99.png)

在/etc/my.cnf开头添加这个参数就ok了

```
skip-grant-tables
```

然后初始化数据库。其中密码在```/etc/jimvc.conf```文件中


```
mysql -u jimv -p8FCHB8R19nrRFtIV < /usr/share/jimv/controller/misc/init.sql
```



大致完整修复过程如下：


```
sed -i '2 iskip-grant-tables'   /etc/my.cnf
systemctl restart mariadb
mysql -u jimv -p8FCHB8R19nrRFtIV < /usr/share/jimv/controller/misc/init.sql

pip install --upgrade pip
pip install -r /usr/share/jimv/controller/requirements.txt
pip install pyjwt
systemctl restart jimvc
```

* 进入配置界面

![20201107_204931_78](image/20201107_204931_78.png)

* 进入登陆界面

![20201107_204952_21](image/20201107_204952_21.png)

![20201107_205030_76](image/20201107_205030_76.png)

* 耍起来~~

## 使用从git拉取源码运行

* 拉取地址：<http://github.com/yifengyou/Jimv-C>

![20201107_201823_15](image/20201107_201823_15.png)

* 如果你去貌似官网的仓库，你会发现，删了几个文件(神操作)...
* 我反正试了，打死跑不起来...应该也许大概很可能正在走向商业化道路
* 老版本还是可以用的，在 ```7c77282ad4ac93cbdf5aa9abdc4ad74cf52586e1```条件前应该可以跑

```
[ -e /usr/share/jimv/controller ] && mv /usr/share/jimv/controller /usr/share/jimv/controller_bak
git clone http://github.com/yifengyou/Jimv-C /usr/share/jimv/controller
```

![20201107_202240_92](image/20201107_202240_92.png)


* 执行INSTALL.sh脚本
* 如果碰到mysql问题，上面有提到解决办法。原因就是mariadb更新了，加了强制安全措施，所以安装脚本可以改改


### 修改配置

下一步，两种选择，一种是编译所有pyc，另一种是，修改service，因为service用的是pyc

1. 编译pyc

```
python -m compileall /usr/share/jimv/controller
```

![20201107_202559_72](image/20201107_202559_72.png)


2. 修改service文件，原来是这样的，用的是/usr/share/jimv/controller/gunicorn_config.pyc

```
# /usr/lib/systemd/system/jimvc.service
[Unit]
Requisite=network-online.target mariadb.service redis.service nginx.service
After=network-online.target network.target mariadb.service redis.service nginx.service

[Install]
WantedBy=multi-user.target

[Service]
PIDFile=/run/jimv/jimvc.pid
Type=idle
User=www
Group=www
RestartSec=2s
ExecStartPre=/usr/bin/mkdir -p /run/jimv
ExecStartPre=/usr/bin/mkdir -p /var/log/jimv
ExecStartPre=/usr/bin/mkdir -p /tmp/jimv
ExecStartPre=/usr/bin/chown -R www.www /run/jimv
ExecStartPre=/usr/bin/chown -R www.www /var/log/jimv
ExecStartPre=-/usr/bin/chown -R www.www /tmp/jimv
ExecStartPre=-/usr/bin/chown -R www.www /var/log/nginx
ExecStartPre=-/usr/bin/chown -R www.www /var/lib/nginx
PermissionsStartOnly=true
#工作目录
WorkingDirectory=/usr/share/jimv/controller/
#命令行(必须使用绝对路径)
ExecStart=/usr/bin/gunicorn -c /usr/share/jimv/controller/gunicorn_config.pyc main:app
#启动或者停止服务最大允许花费60秒
```

这么修改就ok了

```
ExecStart=/usr/bin/gunicorn -c /usr/share/jimv/controller/gunicorn_config.pyc main:app
修改为
ExecStart=/usr/bin/gunicorn -c /usr/share/jimv/controller/gunicorn_config.py main:app
```


### 数据库配置

重要的事情说三遍：

* 我是基于ipxe安装后修改，默认装好后就有mysql等服务。如果你是通过其他途径装的系统，需要执行INSTALL.sh安装哦！！
* 我是基于ipxe安装后修改，默认装好后就有mysql等服务。如果你是通过其他途径装的系统，需要执行INSTALL.sh安装哦！！
* 我是基于ipxe安装后修改，默认装好后就有mysql等服务。如果你是通过其他途径装的系统，需要执行INSTALL.sh安装哦！！

iPXE安装的，没有初始化数据库，那么看下INSTALL.sh怎么操作的

![20201107_202756_85](image/20201107_202756_85.png)



### 安装一些CentOS常用软件

```
yum install -y lrzsz vim htop glances screen tree
```

## 为什么不直接提供源码？而是pyc？？

* 为了优化，好的没问题，我想看源码怎么办
* 不慌，pyc逆向工具带你飞 <https://tool.lu/pyc/>

![20201107_165410_49](image/20201107_165410_49.png)

## 在已有CentOS中安装

在纯净的（仅以 Mini 方式安装，并配置好能连接 Internet 的网络）CentOS 7.6 系统环境中部署

通过在线脚本自动安装 JimV

```
bash -c "$(curl -fsSL http://repo.jimv.cn/jimv.standalone.install.sh)"
```

## 集群部署方案

1. 在 /etc/hosts 文件中布局 JimV 集群

```
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
192.168.10.1    jimvc.jimv.io
192.168.10.2    node01.jimv.io
192.168.10.3    node02.jimv.io
```
2. 通过在线脚本自动安装 JimV-C

```
bash -c "$(curl -fsSL http://repo.jimv.cn/jimvc.install.sh)"
```
3. 根据提示，安装部署 JimV-N

4. 获取系统镜像模板

* 模板下载地址（百度网盘）: <https://pan.baidu.com/s/1V74voI82fGtpgT5P-MED7g#list/path=%2F>
* 跳转连接: <http://template.jimv.cn/>

5. 上传系统镜像模板

存放系统模板到，任意一个计算节点的 /opt/template_images 目录下即可。该目录已经自动做好了计算节点间的 NFS 共享。

6. 创建虚拟机模板

在 JimV-C 控制面板，模板镜像中添加虚拟机模板。

7. 添加 IP 池

在 JimV-C 控制面板，系统配置中添加 IP 池。

8. 享受"简单、快速开"创虚拟机实例的快乐。。。。。



---
