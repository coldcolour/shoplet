1. kv文件说明
一般来说，kv文件中每一行由一个key-value pair组成，根据需求，每个文件的key, value格式各不相同

2. shell脚本以及生成的kv文件的格式说明
(1) user_acts.sh
输出：user_acts.kv
key: U+用户ID+"-ACTS"
value: 一组用;分隔的shop ID:weight
FIXME: taobao_shop_user.shop_id == 1 

从taobao_shop_user, user_doings_info表中导出用户对shop所做的操作，并根据不同操作类型给予一定的打分
用户的操作包括，
A.在taobao_shop_user中的每一行，如果shop_id != 0, 并且，对应的shop_id在taobao_seller_info.taobao_seller_id，且taobao_seller_info.taobao_block == 0,则给予1.0的权重
B.在user_doings_info表中的,doings_type为shop_topic_view, shop_guess, shop_sort_off_time_view, shop_sort_sale_view, shop_sort_time_view, shop_sort_t_view, shop_sort__view之一.

(2) reverse.py
输入：user_acts.kv
输出：shop_actu.kv
把user_acts.kv 转化成，每一行是key-value对，
key: S+shop ID+"_ACTS"
value: 一组用;分隔的user ID:weight, 即，对这个shop有过操作的用户的这些操作的权重

(3) user_actg.sh
输出：user_actg.kv

(4) goods_prop.sh
输出：goods_prop.csv
FIXME: what's the meaning of tgoods_props?

从taobao_goods_ext_info表中导出那些taobao_goods_online_status=1(即商品还在线),且该商品在taobao_goods_info表中也存在的那些商品的属性tgoods_props,且这些商品的创建时间要< WINDOW

(5) prop_json_value.py
输出：goods_prop_value.csv
将goods_prop.csv每一行是key, value对(用\t分隔)，将其中的value部分从json格式解析成python的对象并显示成字符串

(6) goods_tag.sh
输出：goods_tag.csv
取出商品创建时间 < WINDOW 并且仍然还保持online销售的那些商品的tag文本信息，每一个tag单列一行

(7) goods_name.sh
输出：goods_name.csv
从taobao_goods_info表中取出创建时间 < WINDOW 且仍online的那些商品的name的文本信息
格式：goods_id goods_name

(8) goods_rate.sh
输出：goods_rate.csv
从taobao_goods_rates_info导出创建时间 < WINDOW 且仍online的那些商品的用户评论(rate)的文本信息
FIXME: 商品创建时间太短，容易导致没有用户评论

(9) merge_lines.py
先将goods_name.csv, goods_prop_value.csv, goods_rate.cvs, goods_tag.cvs 都输入到同一个文件中，
每一行都是商品的一个文本相关属性，然后将goods_txt按goods_id进行排序，得到的结果是，同一个商品的不同属性被排序到相邻

merge_lines.py 将同一商品的各种文本信息都输出到同一行中

(10) index
用工具pywvtool对商品的文本信息进行分词，得到每个商品的特征向量
输出：goods_index目录
1>goods.tf 按顺序输出每个文档（即每个商品）的文本信息分词以后的term frequency
  格式：doc_id token_id:frequency[ token_id:frequency] (frequency means the occur count in this doc)
2>goods.docinfo 按顺序输出doc_id(从0开始)到商品id的mapping
  格式：doc_id,goods_id
3>中间文件goods.tmp 输出token_id到doc_id的mapping
  格式：token_id,doc_id
4>goods.ii
  将goods.tmp文件先按token_id排序，再按doc_id排序，得到token的doc_frequency(即这个token在多少个文档中出现),然后过滤一些token的doc_frequency过小和过大的token以后，将token重新编号，然后输出new_token_id到a list of doc_id的mapping.
  格式：token_id,doc_frequency(df),doc_id_1,doc_id_2...
5>goods.dic 所有出现在feature vector中的token的列表
  格式：token
FIXME:according to this dump file, the dictionary for segmentation need refinement.
6>goods.corpus 输出这次index的文档数和所有文档中的有效token数
  ocument_count=*
  word_count=*
7>goods.wv 归一化后的token的tf*idf权重向量
  格式：doc_id token_id:weight

(11) classify
为了加快商品相似度的计算，根据商品name的文本信息对商品进行分类，这样在计算相似度的时候，只对本类别的商品进行计算两两相似度, 不过单一商品可以属于多个类别
FIXME:因为该分类方法的recall不是很高，< 50%，因此会有大量的商品分不出来类别，对于这些商品是怎么处理的？
输出：goods_category.csv
	格式：goods_id \t goods_name \t category_name
	      如果某商品属于多个类别，该商品会输出多行
输出：goods_cat.kv
    格式：goods_id   category_name_1[;category_name_2;category_name_3...]
	      每个商品只输出一行
输出：goods.group.1
      将goods_category.csv中goods_id 和category_name打印出来，并且按category_name排序，将同一类别的排到相邻
	格式：goods_id category_name
输出：goods.group.2
      打印所有商品类别名
	格式：category_id(line_number) category_name
输出：goods.group.3
    格式：category_id,goods_id
输出：goods.group
    格式：doc_id \t category_id

(12) cat.words.csv
    格式：

(13) similarity

TODO:
incremental compute similarity
1.导出WINDOW+1天的所有商品信息，其中过去一天的新增商品的相关信息单独存放
2.index
3.classify
4.然后对过去一天的新增商品列表，单独计算这些商品和其他已有商品的相似度
主要的步骤是，看一下mpsmsimi.py脚本，然后写一个计算新增商品和已有商品及他们之间相似度的脚本即可

5.替换现有的字典,根据目前index中分词以后的结果来看，没有出现在字典中的词，都会分成单字，对于我们计算feature vector的时候，其实可以抛弃这些单字，使得feature vector更小，并减少相似度的计算量


GITHUB使用流程
1.从Huang Song的repository hspuppy/shoplet Fork一个repository到coldcolour/shoplet
2.在本地配置github账号
3.clone coldcolour/shoplet到本地
git clone https://github.com/coldcolour/shoplet.git
3.git remote add upsteam https://github.com/hspuppy/shoplet.git
git remote -v
4.本地做了修改以下
git status
git add //将想要commit的文件的变化add
git commit
git push
5.将在coldcolour/shoplet上提交的commit同步到hspuppy
在github的web页面执行"new pull requests"

6.在search服务器上同步code
git fetch origin master
git merge origin/master

7.查看git的配置
git config --list
