#!/bin/sh
# Used to practise kana/kanji->chinese

export LC_COLLATE=C

CUR=`readlink -f $0`
DIR=`dirname $CUR`
cd $DIR
cd ..

# by default we only use lesson files
DICTS=`ls data/dict/lesson1[6-9].dat`
DICTS=$DICTS' '`ls data/dict/lesson2*.dat`
DICTS=$DICTS' '`ls data/dict/lesson3*.dat`

(( $# >= 1)) && DICTS=$*

tail -q --lines=+2 $DICTS  | \
  awk '{
    if (match($3, /^\[.*\]$/)) {
      print $3;
    } else {
      print $2;
    }
  }' | tr -d '[]' | sed '/^[ ]*$/d' | sort | uniq
