#!/bin/sh
# merge selected file into a single dict file

export LC_COLLATE=C

CUR=`readlink -f $0`
DIR=`dirname $CUR`
cd $DIR
cd ..

# by default we only use lesson files
DICTS=`ls data/dict/lesson*.dat`

(( $# >= 1)) && DICTS=$*

echo "#DICT"

tail -q --lines=+2 $DICTS  | \
  awk '{printf("%s %s    %s    %s    %s\n", $1,$2,$3,$4,$5)}' | \
  sort -k2,3 -u | \
  sed '/^[ ]*$/d'
