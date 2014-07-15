#!/bin/bash
source ./config.sh

OUTPUT="../data/goods_sales.kv"
SQL="
SELECT concat('G', tgoods_id, '-PRICE'),
       tgoods_sales_num
FROM taobao_goods_info
WHERE taobao_goods_online_status=1
    AND datediff(curdate(), date(tgoods_create_time))<=90
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT



