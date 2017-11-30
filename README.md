[![License](https://img.shields.io/badge/License-GPL3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0.html)
[![Format](https://img.shields.io/badge/Format-JSON-blue.svg)](http://www.json.org/json-zh.html)
[![Python versions](https://img.shields.io/badge/Python-2.7.10-blue.svg)](https://www.python.org)
[![API](https://img.shields.io/badge/API-RESTful-blue.svg)](http://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)


[TOC]: # "目录"

# 目录
- [项目描述](#项目描述)
- [功能指标](#功能指标)
- [未来计划](#未来计划)
- [安装](#安装)
    - [单机版一键安装](#单机版一键安装)
    - [JimV-C 一键安装](#jimv-c-一键安装)
    - [[JimV-C 手动安装](docs/install.md)](#jimv-c-手动安装)
- [架构图](#架构图)
- [规划与建议](#规划与建议)
    - [配置需求](#配置需求)
    - [网络规划](#网络规划)
    - [计算节点命名](#计算节点命名)
- [问题反馈](#问题反馈)
- [FAQ](#faq)
- [项目成员](#项目成员)
- [JimV 控制平台截图展示](#jimv-控制平台截图展示)
- [Demo](#demo)


## 项目描述

> 计算机硬件越来越白菜价，性能越来越强劲，企业电子信息化方面的业务越来越多，"互联网+"、大数据的浪潮已经掀起，物联网、AI的趋势正在形成。
> 因为上述的一切，虚拟化技术被处于一个软化硬件，揉和硬件与业务系统这么一个核心角色。
> 虚拟化技术虽然已经被普及了很久，但多数企业依然仅仅是把它当做独立的虚拟硬件来使用。在资源的科学分配、高效利用、自动化管理方面，还差些许。
> JimV 是一个，结构清晰简单，易于部署、维护、使用的，低门槛企业私有云管理平台。
> 相比于业界知名的 OpenStack、OpenNebula...，JimV 没有很多的零部件，不需要庞大的维护团队。


## 功能指标

|功能|JimV|
|:-|:-:|
|部署复杂度|低|
|维护复杂度|低|
|KVM虚拟化|✓|
|本地存储|✓|
|共享挂载点|✓|
|GlusterFS|✓|
|Windows Guest|✓|
|Linux Guest|✓|
|Guest 性能统计|✓|
|计算节点性能统计|✓|
|CPU超分|✓|
|内存超分|✓|
|磁盘超配|✓|
|云盘管理|✓|
|云盘热挂载|✓|
|热迁移|✓|
|批量创建|✓|
|RESTful 风格的 API|✓|
|Virtio设备|✓|
|Guest 暂停/恢复|✓|


## 未来计划

>* 增加计费功能
>* 增加 Guest 变配功能
>* 增加过期 Guest 自动回收机制
>* 增加模板上传功能
>* 增加磁盘 IO 限额管理功能
>* 增加磁盘吞吐量限额管理功能
>* 增加网络流量限额管理功能
>* 增加 tag 功能
>* 增加替换 IP 功能
>* 增加对 Ceph 的支持
>* 多租户
>* 用户操作轨迹
>* 用户管理功能
>* 参照 gitlab，打包出 CentOS yum 一语安装仓库
>* 支持快照
>* 支持在线镜像商城
>* 国际化
>* SSH 公钥管理、注入功能
>* 加入移动端的支持


## 安装

### 单机版一键安装
> 在一台服务器上部署 JimV（包含 JimV-C 与 JimV-N）。适合用于本地单机虚拟化作业，或测试等用途。

``` bash
curl https://raw.githubusercontent.com/jamesiter/JimV-C/master/STANDALONE_INSTALL.sh | bash -
```

### JimV-C 一键安装
> 在一台服务器上仅部署 JimV-C。与其它部署 JimV-N 的计算节点一起协同工作。

``` bash
curl https://raw.githubusercontent.com/jamesiter/JimV-C/master/INSTALL.sh | bash -
```

### [JimV-C 手动安装](docs/install.md)


## 架构图
* [JimV 简单应用架构](./topology/JimVSimpleArchitecture.png)
* [JimV 典型应用架构](./topology/JimVRecommendArchitecture.png)

## 规划与建议
> 如下的规划与设计均是以 [JimV 典型应用架构](./topology/JimVRecommendArchitecture.png) 为蓝图。

### 配置需求
**JimV-C**

|条目|指标|备注|
|:-|:-:|:-|
|操作系统| ≥ CentOS 7.4 | 版本过低，所依赖库的功能跟不上。|
|CPU| ≥ 8| 除了 JimV-C 本身的几个功能线程外，MariaDB、Redis 均需要一定量的计算资源。|
|内存| ≥ 16GB | 供 JimV-C、MariaDB、Redis 使用。|
|磁盘| ≥ 500GB | 主要存放计算节点、虚拟机的监控数据及平台的各种日志信息等。|
|互联网络| Y | yum、pip 安装所需要的软件及依赖库时，需要从互联网下载获得。|
|管理网络| Y | 管理计算节点的网络。|
|业务网络| N | 无需通过业务网络和虚拟机接触。|

**JimV-N**

|条目|指标|备注|
|:-|:-:|:-|
|操作系统| ≥ CentOS 7.4 | 版本过低，所依赖库的功能跟不上。|
|CPU| ≥ 36 | 数量直接决定所能承载虚拟机的多少。|
|CPU 虚拟化技术| Y | - |
|内存| ≥ 64GB | - |
|磁盘| ≥ 8TB | 指的是可用空间。建议磁盘组做好 RAID6。|
|磁盘类型| - | 如果是存储密集型，考虑陈本因素，用机械盘就可以了。如果是 IO 密集型，建议 SSD 或 NVME 设备。|
|互联网络| Y | yum、pip 安装所需要的软件及依赖库时，需要从互联网下载获得。|
|管理网络| Y | 管理节点通过改网络传输指令等。|
|业务网络| Y | 虚拟机专用。|
|网卡| ≥ 10Gb x 2端口 x 2网卡 | 网络带宽一般以峰值需求为参考线。高质量的网络可以让使用人员，有更广阔的操作空间。|

**交换机**

|条目|指标|备注|
|:-|:-:|:-|
|数量| 2 | 计算节点上两网卡、两端口相互交叉连接到两个交换机上。以实现网络高可用。|
|LACP| Y | 配合计算节点做 模式4(802.3ad) 的 bonding。|
|接入端口| ≥ 10Gb | 与计算节点网卡做好匹配。|
|端口数量| - | 具体根据计算节点规模来定。|


### 网络规划

**中等规模**

|起止IP|子网掩码|用途|备注|
|:-|:-|:-|:-|
|192.168.1.254|255.255.255.0|业务网络网关地址| - |
|192.168.1.1 ~ 220|255.255.255.0|业务网络虚拟机用| 虚拟机可用 IP 220 个。 |
|192.168.1.221 ~ 252|255.255.255.0|链接虚拟机网卡的，各计算节点网桥地址| 可容纳 32 个计算节点 |
|192.168.2.221 ~ 252|255.255.255.0|计算节点管理地址，与链接虚拟机网卡的网桥地址相对应| - |
|192.168.2.95 ~ 127|255.255.255.0|iDrac 或 iLO 之类的管理地址| - |
|192.168.2.253|255.255.255.0|JimV-C| - |
|192.168.2.254|255.255.255.0|管理网络网关地址| - |


**大规模**

|起始IP|截止IP|子网掩码|用途|备注|
|:-|:-|:-|:-|:-|
|10.10.15.254| - |255.255.240.0|业务网络网关地址| - |
|10.10.1.0|10.10.15.253|255.255.240.0|业务网络虚拟机用| 虚拟机可用 IP 3823 个。 |
|10.10.0.1|10.10.0.253|255.255.240.0|链接虚拟机网卡的，各计算节点网桥地址| 可容纳 253 个计算节点 |
|10.10.16.1|10.10.16.253|255.255.254.0|计算节点管理地址，与链接虚拟机网卡的网桥地址相对应| - |
|10.10.17.1|10.10.17.253|255.255.254.0|iDrac 或 iLO 之类的管理地址| - |
|10.10.16.254| - |255.255.254.0|JimV-C 管理地址| - |
|10.10.17.254| - |255.255.254.0|管理网络网关地址| - |


### 计算节点命名


## 问题反馈

[提交Bug](https://github.com/jamesiter/JimV-C/issues) <br> 技术交流 QQ 群:
377907881

## FAQ
Q1: 出现如下错误该如何解决
> could not find capabilities for arch=x86_64 domaintype=kvm

A1: 检查 BIOS 中 CPU 的 VT 技术是否启用。


## 项目成员

<pre>
姓名:    James Iter
E-Mail: james.iter.cn@gmail.com
</pre>


## JimV 控制平台截图展示

[JimV 控制平台截图展示](docs/screenshot.md)


## Demo

[demo.jimv.io](https://demo.jimv.io) <br>
[jimv.iit.im](https://jimv.iit.im) <br>
管理员账密 `admin`:`jimv.pswd.com`

