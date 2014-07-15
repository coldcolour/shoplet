#!/bin/bash
source ./config.sh

OUTPUT="../data/dict_goods.kv"
SQL="
SELECT tgoods_id FROM taobao_goods_info where taobao_goods_online_status=1 and datediff(curdate(), date(tgoods_create_time))<=90
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT.tmp
paste -d';' -s $OUTPUT.tmp | sed 's/^/DICT-GOODS\t/g' > $OUTPUT
rm $OUTPUT.tmp




