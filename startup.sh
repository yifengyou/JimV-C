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

if [ `id -u` -eq 0 ]; then

    su - www -c "cd ~/sites/JimV-C; gunicorn -c gunicorn_config.py main:app"

elif [ `whoami` = 'www' ]; then

    cd ~/sites/JimV-C; gunicorn -c gunicorn_config.py main:app

else

    echo "Permission denied."
    exit 1

fi

