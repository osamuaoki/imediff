#!/bin/sh -e
# vim: set sw=2 et sw=2 sts=2:
# This is invoked from source tree to test python codes
#
# This is the same as test_unittest_all.py but easier to modify to identify issues from console
# This is not for unittest
#
rm -f imediff.log

PYTHONPATH=$(pwd)/../src
PYTHONPATH=$(realpath $PYTHONPATH)
echo "I: Setting PYTHONPATH=$PYTHONPATH"
export PYTHONPATH

COMMAND="python3 _imediff.py -l"
EXITSTATUS=true
# test 2 file diff
$COMMAND --macro=w -C none -n file_a file_b -o z_imediff2.new
# test 2 file diff
$COMMAND --macro=w -C none -n -f file_a file_b -o z_imediff2_f.new
# test 2 file diff
$COMMAND --macro=w -C none -n -a file_a file_b -o z_imediff2_a.new
# test 2 file diff
$COMMAND --macro=w -C none -n -b file_a file_b -o z_imediff2_b.new
# test 2 file diff
$COMMAND --macro=w -C none -n -d file_a file_b -o z_imediff2_d.new
# test 3 file diff with merge
$COMMAND --macro=w -C none -n file_a file_b file_c -o z_imediff3.new
# test 3 file diff with extra word diff merge
$COMMAND --macro=w -C none -n -a file_a file_b file_c -o z_imediff3_a.new
# test 3 file diff with extra word diff merge
$COMMAND --macro=w -C none -n -b file_a file_b file_c -o z_imediff3_b.new
# test 3 file diff with extra word diff merge
$COMMAND --macro=w -C none -n -c file_a file_b file_c -o z_imediff3_c.new
# test 3 file diff with extra word diff merge
$COMMAND --macro=w -C none -n -d file_a file_b file_c -o z_imediff3_d.new
# test 3 file diff with extra word diff merge
$COMMAND --macro=w -C none -n -f file_a file_b file_c -o z_imediff3_f.new
# test 3 file diff with extra word diff merge
$COMMAND --macro=w -C none -n -g file_a file_b file_c -o z_imediff3_g.new
echo
ls -l *.new
for f in *.new; do
	g="${f%.new}.ref"
	echo " ==== COMPARE: $g vs. $f ==="
	if diff -u "$g" "$f"; then
		echo " -> = NO_DIFF: $g"
	else
		echo " -> ! DIFF: $g"
		EXITSTATUS=false
	fi
	echo
done
$EXITSTATUS
