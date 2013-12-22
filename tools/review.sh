#!/bin/sh
# Try to catch words which fails frequently.
# Currently, it make uses top 50 fails from 
# the logfile
# The fail rate is defined as: sqrt(fail) / pass

# How many fallible words to review
TOPN=50

# LC_COLLATE:
# "This variable determines the locale category for character collation. 
#  It determines collation information for regular expressions and sorting, 
#  including equivalence classes and multi-character collating elements..."
#
export LC_COLLATE=C

# get to right directory
CUR=`readlink -f $0`
DIR=`dirname $CUR`
cd $DIR
cd ..

FULL=`mktemp`
PART=`mktemp`
HARD=`mktemp`
JOIN=`mktemp`

# by default we only use lesson files
DICTS=data/dict/lesson*.dat

(( $# >= 1)) && DICTS=$*

# get full dicts 
tail -q --lines=+2 $DICTS  | \
  sed '/^$/d'              | \
  sort -k2 > $PART

# calculate fallible rate 
tail -q --lines=+2 log/dict.im.dat | \
  awk '{print $3, sqrt($2)/$1}'    | \
  sort -k1 > $FULL

# restrict words to be from DICT
join -1 1 -2 2 $FULL $PART               | \
  sort -grk2                             | \
  awk '{printf "%s [%0.2f]\n", $1, $2}'  | \
  head -$TOPN                            | \
  sort -k1 > $HARD

# fake dict head
echo "#DICT" > $JOIN

join -1 2 -2 1 $PART $HARD | awk '{t=$1;$1=$2;$2=t;print}' >> $JOIN

rm -f $FULL $PART $HARD

./dict.py $JOIN

rm -f $JOIN 
