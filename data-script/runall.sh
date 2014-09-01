#!/bin/bash

for script in dict_shop.sh dict_user.sh dict_goods goods_binfo.sh goods_price.sh goods_sales.sh shop_binfo.sh shop_favu.sh shop_goods.sh user_actg.sh user_acts.sh user_favg.sh user_favs.sh goods_tag.sh goods_name.sh goods_rate.sh goods_prop.sh;
do
	echo $script
	time . ./$script
done

echo shop_actu
python reverse.py ../data/user_acts.kv SXX_ACTU > ../data/shop_actu.kv
echo goods_actu
python reverse.py ../data/user_actg.kv GXX_ACTU > ../data/goods_actu.kv
echo goods_prop_value
python prop_json_value.py ../data/goods_prop.csv > ../data/goods_prop_value.csv
echo goods_txt
cat ../data/goods_name.csv ../data/goods_prop_value.csv ../data/goods_rate.csv ../data/goods_tag.csv > ../data/goods_txt
sort -k1,1n -o ../data/goods_txt ../data/goods_txt 
python merge_lines.py ../data/goods_txt ../data/foo && mv ../data/foo ../data/goods_txt
echo classify
python ../mining/classify.py ../data/goods_name.csv ../data/catwords.tsv > ../data/goods_category.csv
echo index
python ../../pywvtool/pywvtool.py -t goods -o ../data/goods_index --loader="LocalKVFileLoader" --loader-op="src=../data/goods_txt" --tokenizer="MMSegTokenizer" -w TFIDF
