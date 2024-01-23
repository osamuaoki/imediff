#!/bin/sh -e
# vim: set sw=2 et sw=2 sts=2:
CONTINUE_TEST=false
if [ "$1" = "-t" ]; then
  CONTINUE_TEST=true
fi
EXITSTATUS=true
./_diff23.py >z_diff23.new
./_imediff.py  -C BOGUS -n file_a file_b -o z_imediff2.new
./_imediff.py -C BOGUS -n file_a file_b file_c -o z_imediff3.new
./_imediff.py -C BOGUS -n -f file_a file_b file_c -o z_imediff3_f.new
./_initialize.py  > z_initialize.new
./_macrotrans.py -C alternative_imediff.conf -n file_a file_b file_c > z_macrotrans.new
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
