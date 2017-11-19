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
- [架构流程图](#架构流程图)
- [问题反馈](#问题反馈)
- [项目成员](#项目成员)
- [Web端程序截图](#web端程序截图)
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


## 架构流程图


## 问题反馈

[提交Bug](https://github.com/jamesiter/JimV-C/issues) <br> 技术交流 QQ 群:
377907881


## 项目成员

<pre>
姓名:    James Iter
E-Mail: james.iter.cn@gmail.com
</pre>


## Web端程序截图

[Web端程序截图](docs/screenshot.md)


## Demo

[demo.jimv.io](https://demo.jimv.io) <br> 管理员账密 `admin`:`jimv.pswd.com`

