#!/bin/bash
source ./config.sh
if [[ -z "$WINDOW" ]];
then
    WINDOW=90
fi

OUTPUT="../data/goods_rate.csv"
SQL="
SELECT ri.tgoods_id,
       rates_txt
FROM taobao_goods_rates_info ri
	JOIN taobao_goods_info gi ON gi.tgoods_id=ri.tgoods_id
WHERE taobao_goods_online_status=1
    AND datediff(curdate(), date(tgoods_create_time))<=$WINDOW
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




