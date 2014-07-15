#!/bin/bash
source ./config.sh

OUTPUT="../data/shop_binfo.kv"
SQL="
select concat('S',shop.taobao_shop_id,'-BINFO'), 
	concat('title:',taobao_shop_title,';domain:',shop.taobao_shop_domain,
		';borc:',taobao_type,';block:',taobao_block,';like:',taobao_shop_like_num) 
from taobao_shop_info shop
     join taobao_seller_info seller on seller.taobao_seller_id=shop.taobao_seller_id
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




