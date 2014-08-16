#!/bin/bash
cd ../../pywvtool
python pywvtool.py -t goods -o /home/web/shoplet/data/goods_index --loader="LocalKVFileLoader" --loader-op="src=/home/web/shoplet/data/goods_txt" --tokenizer="MMSegTokenizer" -w TFIDF
