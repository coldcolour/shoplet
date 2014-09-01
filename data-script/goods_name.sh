#!/bin/bash
source ./config.sh
if [[ -z "$WINDOW" ]];
then
    WINDOW=90
fi

OUTPUT="../data/goods_name.csv"
SQL="
SELECT tgoods_id,tgoods_name
FROM taobao_goods_info gi
WHERE taobao_goods_online_status=1
    AND datediff(curdate(), date(tgoods_create_time))<=$WINDOW
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




