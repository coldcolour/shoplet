#!/bin/bash
source ./config.sh

OUTPUT="../data/goods_name.csv"
SQL="
SELECT tgoods_id,tgoods_name
FROM taobao_goods_info gi
WHERE taobao_goods_online_status=1
    AND datediff(curdate(), date(tgoods_create_time))<=90
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




