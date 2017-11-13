#!/bin/bash

# Author: James.Iter
# Comment: Generate random password!
# Date: Mon Dec 30 17:54:18 CST 2013

PSWD_FACTOR=(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z \
       a b c d e f g h i j k l m n o p q r s t u v w x y z 1 2 3 4 5 6 7 8 9 0)
FACTOR_LEN=${#PSWD_FACTOR[*]}
PSWD_LEN=16;
PSWD="";

if [ $# -eq 1 ]; then
    PSWD_LEN=$1
fi

function gen_pswd() {
    for ((i=1;i<=${PSWD_LEN};i++));
    do
        PSWD="${PSWD}"${PSWD_FACTOR[$((RANDOM%FACTOR_LEN))]}
    done
}

gen_pswd
echo -n ${PSWD}

