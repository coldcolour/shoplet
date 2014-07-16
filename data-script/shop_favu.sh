#!/bin/bash
source ./config.sh

OUTPUT="../data/shop_favu.kv"
SQL="
select concat('S', shop_id, '-FAVU'), group_concat(user_id separator ';') as uids
from taobao_shop_user su
     join taobao_seller_info seller on seller.taobao_seller_id=su.shop_id
where shop_id <> 1 and seller.taobao_block=0
group by shop_id;
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




