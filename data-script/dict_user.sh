#!/bin/bash
source ./config.sh

OUTPUT="../data/dict_user.kv"
SQL="
select distinct user_id from user_info;
"

$MYSQL -N -h $HOST -D $DB --password=$PASS $OTHER -e "$SQL" > $OUTPUT.tmp
paste -d';' -s $OUTPUT.tmp | sed 's/^/DICT-USER\t/g' > $OUTPUT
rm $OUTPUT.tmp



