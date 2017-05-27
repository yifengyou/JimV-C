# TODO

- 添加对 Guest 的IP管理功能
> 1. 给宿主机替换当前 IP 池中可用的 IP。替换后，新 IP 置为已用状态，被替换的 IP，
> 要与系统配置中的可用 IP 范围做计算。计算其是不是可以被自动分配的合法 IP。如果是，
> 则回收。如果不是，则直接丢弃；
> 2. 给宿主机替换手动指定的任意 IP。此时需要判断手动分配的 IP 是否与已用的 IP 冲突；

- os_init_write 的更新方法里，是否需要支持 os_init_id 参数
- 增加模板镜像上传功能
- 抽象出视图层的父类，尤其是 get、get_list、delete 这些方法基本相同
- guest_disk 表中加入 path 字段，具体磁盘位置由 path 指明
- guest 的系统磁盘，也需记录到 guest_disk 表中
- os_template 表中 name 改为 path 字段。又 path 指明完整路径
