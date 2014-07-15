#!/bin/bash
source ./config.sh

OUTPUT="../data/user_acts.kv"
SQL="
select concat('U', user_id, '-ACTS'), group_concat(concat(shop_id, ':', w) separator ';') from
(

SELECT user_id,
       shop_id,
       Sum(weight) AS w
FROM   (SELECT user_id,
               shop_id,
               1.0 AS weight
        FROM   taobao_shop_user su
               JOIN taobao_seller_info seller
                 ON seller.taobao_seller_id = su.shop_id
        WHERE  shop_id <> 1
               AND seller.taobao_block = 0
        UNION
        SELECT user_id,
               doings_value_1 AS shop_id,
               ( CASE doings_type
                   WHEN 'shop_topic_view' THEN 0.2
                   WHEN 'shop_guess' THEN 0.3
                   WHEN 'shop_sort_off_time_view' THEN 0.2
                   WHEN 'shop_sort_sale_view' THEN 0.2
                   WHEN 'shop_sort_time_view' THEN 0.2
                   WHEN 'shop_sort_t_view' THEN 0.2
                   WHEN 'shop_sort__view' THEN 0.2
                 END )        AS weight
        FROM   user_doings_info
        WHERE  doings_type = 'shop_guess'
                OR doings_type LIKE 'shop%view') a
GROUP  BY user_id,
          shop_id
) b
group by user_id;
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




