#!/bin/bash
source ./config.sh

OUTPUT="../data/user_favs.kv"
SQL="
select concat('U', user_id, '-FAVS'), group_concat(shop_id separator ';') as sids
from taobao_shop_user su
     join taobao_seller_info seller on seller.taobao_seller_id=su.shop_id
where shop_id <> 1 and seller.taobao_block=0
group by user_id;
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




