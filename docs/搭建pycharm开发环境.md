# 搭建pycharm开发环境

## 选择jimv v0.8版本

* 比较老，最初开源的版本


![20201107_221627_64](image/20201107_221627_64.png)



## pycharm构建远程开发

![20201107_221726_33](image/20201107_221726_33.png)


* 构建一个virtual python虚拟环境

```
pip install virtualenv
virtualenv python2env
```

![20201107_222217_65](image/20201107_222217_65.png)

```
source python2env/bin/activate

pip install -r requirements.txt
```

* 启用虚拟环境，安装依赖

![20201107_222402_42](image/20201107_222402_42.png)

![20201107_222443_34](image/20201107_222443_34.png)

![20201107_222515_71](image/20201107_222515_71.png)

![20201107_223427_22](image/20201107_223427_22.png)

* 不要同步python2env虚拟环境

![20201107_223457_59](image/20201107_223457_59.png)

* 从服务器同步文件

![20201107_223550_57](image/20201107_223550_57.png)

![20201107_223620_42](image/20201107_223620_42.png)

* 配置自动上传

![20201107_223641_39](image/20201107_223641_39.png)

---
