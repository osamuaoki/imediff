#!/bin/sh -e
# vim: set sw=2 et sw=2 sts=2:
# This is invoked from source tree to test python codes
rm -f imediff.log

PYTHONPATH=$(pwd)/../src
PYTHONPATH=$(realpath $PYTHONPATH)
echo "I: Setting PYTHONPATH=$PYTHONPATH"
export PYTHONPATH

EXITSTATUS=true
python3 _imediff.py -D -C BOGUS -n file_a file_b -o z_imediff2.new
python3 _imediff.py -D -C BOGUS -n file_a file_b file_c -o z_imediff3.new
python3 _imediff.py -D -C BOGUS -n -f file_a file_b file_c -o z_imediff3_f.new
python3 _diff23.py > z_diff23.new
python3 _initialize.py  > z_initialize.new
python3 _macrotrans.py -C alternative_imediff.conf -n file_a file_b file_c > z_macrotrans.new
for f in *.new; do
  g="${f%.new}.ref"
  echo " ==== COMPARE: $g vs. $f ==="
  if diff -u "$g" "$f" ; then
    echo " -> = NO_DIFF: $g"
  else
    echo " -> ! DIFF: $g"
    EXITSTATUS=false
    $CONTINUE_TEST
  fi
  echo
done
$EXITSTATUS
