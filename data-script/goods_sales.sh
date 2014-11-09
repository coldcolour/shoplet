#!/bin/bash
source ./config.sh
if [[ -z "$WINDOW" ]];
then
    WINDOW=90
fi

OUTPUT="../data/goods_sales.kv"
SQL="
SELECT concat('G', tgoods_id, '-SALES'),
       tgoods_sales_num
FROM taobao_goods_info
WHERE taobao_goods_online_status=1
    AND datediff(curdate(), date(tgoods_create_time))<=$WINDOW
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




