#!/usr/bin/env bash
#
# JimV-C
#
# Copyright (C) 2017 JimV <james.iter.cn@gmail.com>
#
# Author: James Iter <james.iter.cn@gmail.com>
#
#  Shutdown the JimV-C.

systemctl stop jimvc.service
systemctl status jimvc.service -l

# 服务结束后，/run/jimv/jimvc.pid 文件会被 gunicorn 自动清除。如果该文件还存在，则表示服务依然活着。
# 在执行 systemctl stop 后，若服务任然活着，则强制结束。
if [ -f '/run/jimv/jimvc.pid' ]; then
    if [ -f '/run/jimv/jimvc.pid' ]; then

        killall -9 gunicorn
        rm -f /run/jimv/jimvc.pid
        echo 'JimV-C is forced to terminate.';
        exit 1

    fi
fi

if [ ! -e '/run/jimv/jimvc.pid' ]; then
    echo 'JimV-C stopped.';
fi

