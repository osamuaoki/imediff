#!/bin/sh
# vim: set sw=2 et sw=2 sts=2:
export PYTHONPATH=../src

./_diff23.py >z_diff23.new
./_imediff.py  -C BOGUS -n file_a file_b -o z_imediff2.new
./_imediff.py -C BOGUS -n file_a file_b file_c -o z_imediff3.new
./_initialize.py  > z_initialize.new
./_macrotrans.py -C alternative_imediff.conf -n file_a file_b file_c > z_macrotrans.new
for f in *.new; do
  g="${f%.new}.ref"
  echo " ==== COMPARE: $g vs. $f ==="
  diff -u "$g" "$f" && echo " -> = NO_DIFF: $g" || echo " -> ! DIFF: $g"
  echo
done
