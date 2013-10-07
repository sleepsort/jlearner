#!/bin/sh
function usage() {
  echo "  Remove bogus whitespace from file"
  echo "  usage:"
  echo "    $0 [file name]"
  exit 1
}
(( $# == 1 )) || usage
sed -i 's/　/  /g' $1
