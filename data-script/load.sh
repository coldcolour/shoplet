#!/bin/bash
STAGE_TABLE=goods_recommend_goods_stage
TMP_TABLE=goods_recommend_goods_tmp
REAL_TABLE=goods_recommend_goods

echo "Loading data..."

PA=`pwd`
SQL="TRUNCATE TABLE $STAGE_TABLE;
LOAD DATA LOCAL INFILE '$PA/../data/goods.filtered.simi' INTO TABLE $STAGE_TABLE FIELDS TERMINATED BY '\t' (goods_id, goods_list);
RENAME TABLE $REAL_TABLE TO $TMP_TABLE, $STAGE_TABLE TO $REAL_TABLE, $TMP_TABLE TO $STAGE_TABLE;
"
mysql -h 188.188.188.20 --password="XVfM<\$8{/\$yb" -uroot -D youjiaxiaodian_com --default-character-set=utf8 -e "$SQL"

echo "Loading data...DONE"
