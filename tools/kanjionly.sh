#!/bin/sh
# Try to catch words with 'Kanji', so 
# that by providing Kanji as hints, we 
# can practise how kanji are pronounced
# in Japanese

export LC_COLLATE=C

TEMP=`mktemp`

CUR=`readlink -f $0`
DIR=`dirname $CUR`
cd $DIR
cd ..

# by default we only use lesson files
DICTS=data/dict/lesson*.dat

(( $# >= 1)) && DICTS=$*

echo "#DICT" > $TEMP

# get words with kanji
tail -q --lines=+2 $DICTS  | \
  sed '/^$/d'              | \
  grep "\[[^ ]*\]"         | \
  awk '{print $1,$2,$3}'   | \
  tr -d '[]' >> $TEMP

./dict.py $TEMP

rm -f $TEMP
