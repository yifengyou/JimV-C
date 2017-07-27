# TODO

- [x] Guest 删除后，回收其 IP、VNC 端口
- [x] os_init_write 的更新方法里，支持 os_init_id 参数
- [x] 抽象出视图层的父类，尤其是 get、get_list、delete 这些方法基本相同
- [x] guest_disk 表中加入 path 字段，具体磁盘位置由 path 指明
- [x] guest 的系统磁盘，也需记录到 guest_disk 表中
- [x] 将 Guest 的系统镜像合并到单独的磁盘镜像目录中。即不再为 Guest 的系统镜像单独分配目录
- [x] os_template 表中 name 改为 path 字段。用 path 指明完整路径
- [x] 统一 guest_disk 称谓为 disk
- [x] 统计活着的宿主机，并提供获取列表的接口，供迁移时选择
- [x] 分离出 API 与 views 出入口，涉及 add_rule 与 route_table
- [x] 加入被动更新 Guest xml 的功能，由宿主机主动推送。具体时机待定
- [x] 重置Guest密码功能
- [ ] 增加模板镜像上传功能
- [x] 虚拟机加入用户级的重启作业功能
- [ ] 提示待做的启动作业
- [ ] 加入 tag 功能
- [ ] 收集存在于 JimV-N，却不存在于 JimV-C 的 Guest
- [x] 批量添加启动作业
- [ ] 单独写页面展现已有启动作业的虚拟机列表
- [x] 磁盘页面，默认不显示系统盘，加 CheckBox 来控制
- [x] 不显示系统级别的启动作业
- [ ] 添加对 Guest 的IP管理功能
- [ ] 设计、制作替换 Guest IP 的系统级启动作业
> 1. 给宿主机替换当前 IP 池中可用的 IP。替换后，新 IP 置为已用状态，被替换的 IP，
> 要与系统配置中的可用 IP 范围做计算。计算其是不是可以被自动分配的合法 IP。如果是，
> 则回收。如果不是，则直接丢弃；
> 2. 给宿主机替换手动指定的任意 IP。此时需要判断手动分配的 IP 是否与已用的 IP 冲突；
