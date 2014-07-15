#!/bin/bash
source ./config.sh

OUTPUT="../data/user_favg.kv"
SQL="
select concat('U', user_id, '-FAVG'), group_concat(tgoods_id separator ';') as gids
from taobao_goods_user
group by user_id;
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




