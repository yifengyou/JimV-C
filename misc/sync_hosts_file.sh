#!/usr/bin/env bash
#
# JimV-C
#
# Copyright (C) 2017 JimV <james.iter.cn@gmail.com>
#
# Author: James Iter <james.iter.cn@gmail.com>
#
#  Sync the /etc/hosts file.
#

DHOSTS=`egrep -v '^$|localhost|jimvc' /etc/hosts | awk '{ print $1; }'`

for dhost in ${DHOSTS}
do
    scp /etc/hosts ${dhost}:/etc/hosts
done

