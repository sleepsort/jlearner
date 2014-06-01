#!/bin/sh
# Try to catch words with 'Kanji', so 
# that by providing Kanji as hints, we 
# can practise how they are pronounced
# in Japanese

export LC_COLLATE=C

TEMP=`mktemp`

CUR=`readlink -f $0`
DIR=`dirname $CUR`
cd $DIR
cd ..

# by default we only use lesson files
DICTS=`ls data/dict/lesson1[6-9].dat`
DICTS=$DICTS' '`ls data/dict/lesson2*.dat`
DICTS=$DICTS' '`ls data/dict/lesson3*.dat`

(( $# >= 1)) && DICTS=$*

echo "#DICT" > $TEMP

tail -q --lines=+2 $DICTS  | \
  sed '/^$/d'              | \
  grep "\[[^ ]*\]"         | \
  tr -d '[]'               | \
  awk '{
    if (match($4, /^<[^ ]*>$/)) {
      print $1,$2,$4,$3;
    } else {
      print $1,$2,$3;
    }
  }' >> $TEMP

./dict.py $TEMP

rm -f $TEMP
