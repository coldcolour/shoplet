#!/bin/bash
source ./config.sh

OUTPUT="../data/user_actg.kv"
SQL="
SELECT concat('U', user_id, '-ACTG'),
       group_concat(concat(goods_id, ':', w) separator ';')
FROM
    ( SELECT user_id,
             goods_id,
             sum(weight) AS w
     FROM
         (SELECT user_id,
                 tgoods_id AS goods_id,
                 1.0 AS weight
          FROM taobao_goods_user
          UNION SELECT user_id,
                       doings_value_1 AS goods_id,
                       (CASE doings_type WHEN 'goods_detail_image' THEN 0.2 WHEN 'goods_topic_review' THEN 0.1 WHEN 'goods_view' THEN 0.1 WHEN 'goods_view_taobao' THEN 0.3 END) AS weight
          FROM user_doings_info
          WHERE doings_type IN ('goods_detail_image',
                                'goods_topic_review',
                                'goods_view',
                                'goods_view_taobao')
          UNION SELECT user_id,
                       t.tgoods_id AS goods_id,
                       (CASE doings_type WHEN 'goods_cart_taobao' THEN 0.2 WHEN 'goods_fav_taobao' THEN 0.2 WHEN 'goods_order_taobao' THEN 0.3 END) AS weight
          FROM user_doings_info u
          JOIN taobao_goods_info t ON u.doings_value_1=t.taobao_goods_id
          WHERE doings_type IN ('goods_cart_taobao',
                                'goods_fav_taobao',
                                'goods_order_taobao')) a
     GROUP BY user_id,
              goods_id ) b
GROUP BY user_id;
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT




