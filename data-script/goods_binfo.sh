#!/bin/bash
source ./config.sh
if [[ -z "$WINDOW" ]];
then
    WINDOW=90
fi

OUTPUT="../data/goods_binfo.kv"
SQL="
SELECT concat('G',tgoods_id,'-BINFO'),
       concat('name:',tgoods_name,';shop:',shop_id,';like:',tgoods_like_num,';age:',datediff(curdate(),date(tgoods_create_time)),';tbid:',taobao_goods_id,';imgurl:',taobao_goods_image_url)
FROM taobao_goods_info
WHERE taobao_goods_online_status=1
    AND datediff(curdate(), date(tgoods_create_time))<=$WINDOW
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




