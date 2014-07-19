#!/bin/bash

for script in dict_shop.sh dict_user.sh goods_binfo.sh goods_price.sh goods_sales.sh shop_binfo.sh shop_favu.sh shop_goods.sh user_actg.sh user_acts.sh user_favg.sh user_favs.sh;
do
	echo $script
	time . ./$script
done

python reverse.py ../data/user_acts.kv > ../data/shop_actu.kv
	
