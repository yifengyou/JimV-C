# 枚举列表

[TOC]: # "目录"

# 目录
- [Guest 状态](#guest-状态)
- [磁盘状态](#磁盘状态)


## Guest 状态
|状态|值|描述|
|:--:|:--:|:--:|
|no_state|0|无任何状态，一般是在创建Guest时会出现。|
|running|1|Guest运行中。|
|blocked|2|Guest阻塞。|
|paused|3|Guest被暂停。|
|shutdown|4|Guest关机状态。|
|shutoff|5|Guest切断电源状态。|
|crashed|6|Guest奔溃状态。|
|pm_suspended|7|电源被悬挂。|
|dirty|255|Guest现场被弄脏，需要清理。|


## 磁盘状态
|状态|值|描述|
|:--:|:--:|:--:|
|pending|0|创建磁盘时的未决状态。|
|idle|1|空闲状态，未被任何Guest使用。|
|mounted|2|已经被某个Guest所挂载。|
|dirty|255|磁盘创建失败，需要被清理。|

