#!/usr/bin/env bash
#
# JimV-C
#
# Copyright (C) 2017 JimV <james.iter.cn@gmail.com>
#
# Author: James Iter <james.iter.cn@gmail.com>
#
#  Start up the JimV-C.
#

id www >& /dev/null

if [ $? -ne 0 ]; then
    echo "Please install JimV-C before."
    exit 1
fi

systemctl start jimvc.service
systemctl status jimvc.service -l

