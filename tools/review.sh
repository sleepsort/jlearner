#!/bin/sh
# Try to catch words which fails frequently.
# Currently, it make uses top 50 fails from 
# the logfile

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
HEAD=`mktemp`
HARD=`mktemp`

# get full dicts 
tail -q --lines=+2 data/dict/*.dat | sed '/^$/d' | sort -k2 > $FULL

# get most fallible words
tail -q --lines=+2 log/dict.im.dat | sort -nrk2 | head -50 | awk '{print $3}' | sort -k1 > $HEAD

# steal the dict head
cat data/dict/*.dat | head -1 > $HARD

# join and get a fake dictionary, containing most fallible words
join -1 1 -2 2 $HEAD $FULL | awk '{t=$1;$1=$2;$2=t;}1' >> $HARD

rm -f $HEAD $FULL

./dict.py $HARD

rm -f $HARD 
