#!/bin/bash
cd ..
. env.sh
cd data-script

for script in dict_shop.sh dict_user.sh dict_goods.sh goods_binfo.sh goods_price.sh goods_sales.sh shop_binfo.sh shop_favu.sh shop_goods.sh user_actg.sh user_acts.sh user_favg.sh user_favs.sh goods_tag.sh goods_name.sh goods_rate.sh goods_prop.sh;
do
	echo $script
	time . ./$script
done

echo shop_actu
pypy reverse.py ../data/user_acts.kv SXX_ACTU > ../data/shop_actu.kv
echo goods_actu
pypy reverse.py ../data/user_actg.kv GXX_ACTU > ../data/goods_actu.kv
echo goods_prop_value
pypy prop_json_value.py ../data/goods_prop.csv > ../data/goods_prop_value.csv
echo goods_txt
cat ../data/goods_name.csv ../data/goods_prop_value.csv ../data/goods_rate.csv ../data/goods_tag.csv > ../data/goods_txt
sort -k1,1n -o ../data/goods_txt ../data/goods_txt 
pypy merge_lines.py ../data/goods_txt ../data/foo && mv ../data/foo ../data/goods_txt

echo index
time python ../../pywvtool/pywvtool.py -t goods -o ../data/goods_index --loader="LocalKVFileLoader" --loader-op="src=../data/goods_txt" --tokenizer="MMSegTokenizer" -w TFIDF

echo classify
time pypy ../mining/classify2.py ../data/goods_name.csv ../data/cat.words.csv > ../data/goods_category.csv
gawk -F'\t' '{printf("G%s-CAT\t%s\n",$1,$3)}' ../data/goods_category.csv | gawk -F "\t" 's != $1 || NR ==1{s=$1;if(p){print p};p=$0;next}{sub($1,"",$0);p=p""$0;}END{print p}' | sed 's/	/;/g;s/;/	/1' > ../data/goods_cat.kv
#pypy ../mining/classify2.py ../data/goods_name.csv ../data/catwords.tsv > ../data/goods_category.csv
gawk -F'\t' '{print $1,$3}' ../data/goods_category.csv | sed 's/:.*$//g' | sort -k2,2 > ../data/goods.group.1
#gawk -F'\t' '{print $1}' ../data/catwords.tsv | cat -n | sed 's/ //g;s/\t/ /g' | sort -k2,2 > ../data/goods.group.2
gawk -F',' '{print $1}' ../data/cat.words.csv | cat -n | sed 's/ //g;s/\t/ /g' | sort -k2,2 > ../data/goods.group.2
join -j 2 ../data/goods.group.1 ../data/goods.group.2 | gawk '{printf "%d,%d\n",$3,$2}' | sort -t, -k2,2 > ../data/goods.group.3
join -t, -j 2 ../data/goods_index/goods.docinfo ../data/goods.group.3 | awk -F, '{printf "%d\t%d\n",$2,$3}' > ../data/goods.group
rm ../data/goods.group.*

echo simi
cd ../mining
time pypy mpsmsimi.py ../data/goods_index/goods.wv ../data/goods.simi ../data/goods.group

echo filter
time pypy filter_simi.py ../data/goods.simi ../data/goods_index/goods.docinfo ../data/goods_name.csv ../data/name.me ../data/goods.filtered.simi

echo sample
shuf -n 50 ../data/goods.filtered.simi > ../data/goods.simi.sample

echo sample html page
python goods_simi_demo.py ../data/goods.simi.sample ../data/goods_index/goods.docinfo ../data/goods.sample.html

cd ../data-script

if [ -e data/goods.filtered.simi.lastdays ]; then
    echo lastdays data
    rm data/goods.filtered.simi.lastdays
fi

echo load
./load.sh

echo all done
