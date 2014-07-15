#!/bin/bash
source ./config.sh

OUTPUT="../data/shop_goods.kv"
SQL="
SELECT concat('S',shop_id,'-GOODS'),
       group_concat(tgoods_id separator ';')
FROM taobao_goods_info
WHERE taobao_goods_online_status=1
    AND datediff(curdate(), date(tgoods_create_time))<=90
GROUP BY shop_id
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




