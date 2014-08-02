#!/bin/bash
source ./config.sh

OUTPUT="../data/goods_tag.csv"
SQL="
SELECT tr.tgoods_id, ti.goods_tag_name
FROM goods_tag_relation tr
	join taobao_goods_info gi on gi.tgoods_id=tr.tgoods_id
	join goods_tag_info ti on tr.goods_tag_id=ti.goods_tag_id
WHERE taobao_goods_online_status=1
    AND datediff(curdate(), date(tgoods_create_time))<=90
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




