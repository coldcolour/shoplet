#!/bin/bash
source ./config.sh
if [[ -z "$WINDOW" ]];
then
    WINDOW=90
fi

OUTPUT="../data/goods_price.kv"
SQL="
SELECT concat('G', tgoods_id, '-PRICE'),
       tgoods_sale_price
FROM taobao_goods_info
WHERE taobao_goods_online_status=1
    AND datediff(curdate(), date(tgoods_create_time))<=$WINDOW
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




