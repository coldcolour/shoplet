#!/bin/bash
source ./config.sh

OUTPUT="../data/dict_shop.kv"
SQL="
SELECT taobao_shop_id FROM taobao_shop_info
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT.tmp
paste -d';' -s $OUTPUT.tmp | sed 's/^/DICT-SHOP\t/g' > $OUTPUT
rm $OUTPUT.tmp




