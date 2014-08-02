#!/bin/bash
source ./config.sh

OUTPUT="../data/goods_prop.csv"
SQL="
SELECT ei.tgoods_id,
       tgoods_props
FROM taobao_goods_ext_info ei
	JOIN taobao_goods_info gi ON gi.tgoods_id=ei.tgoods_id
WHERE taobao_goods_online_status=1
    AND datediff(curdate(), date(tgoods_create_time))<=90
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




