#!/bin/sh
function usage() {
  echo "  Remove bogus whitespace from file"
  echo "  usage:"
  echo "    $0 [file names]"
  exit 1
}
(( $# >= 1 )) || usage
for x in $*;
do
  sed -i 's/　/  /g' $x
done
